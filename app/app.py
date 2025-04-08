import os
import yaml
import shutil
import httpx
import uvicorn
import asyncio
from utils import Utils
from pathlib import Path
from loguru import logger
from trainer import Trainer
from pydantic import BaseModel
from kidfinder import KidFinder
from fastapi_cache import FastAPICache
from fastapi.templating import Jinja2Templates
from fastapi_cache.decorator import cache
from whatsapp_api_client_python import API
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from models.trainrequest import TrainRequest
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_cache.backends.inmemory import InMemoryBackend
from whatsapp_chatbot_python import GreenAPIBot, Notification
from fastapi import FastAPI, Request, HTTPException, Depends, Header, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize the in-memory cache.
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    # Shutdown: perform any cleanup if required (none needed here).
  

# Configuration
utils = Utils()
utils.create_application_folders()
utils.load_config()

greenAPI = API.GreenAPI(os.getenv("GREEN_API_INSTANCE"), os.getenv("GREEN_API_TOKEN"))
bot = GreenAPIBot(os.getenv("GREEN_API_INSTANCE"), os.getenv("GREEN_API_TOKEN"))
app = FastAPI(lifespan=lifespan)
app.mount("/images/trainer", StaticFiles(directory=os.path.join("images", "trainer")), name="trainer_images")
templates = Jinja2Templates(directory="templates")

# Rekognition classes
trainer = Trainer()
finder = KidFinder()



class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"


@bot.router.message()
def message_handler(notification: Notification) -> None:
    utils.get_message_data(notification.event)
    if utils.is_image:
        collection_id = utils.get_collection_id()
        if collection_id is not None:
            if utils.download_image(collection_id):
                success = finder.find(collection_id=collection_id, image_path=utils.download_path,label=collection_id)
                if success:
                    logger.info(f"{collection_id} was detected in the image.")
                    notification.api.sending.forwardMessages(utils.config.get("target"),utils.chat_id,[utils.message_id])
                    
                else:
                    logger.info(f"{collection_id} was not detected in the image.")
                os.remove(utils.download_path)    


@app.post("/train", response_class=JSONResponse)
async def train_model(
    collection: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Endpoint to upload an image and trigger model training.

    - **collection**: The collection id as a form field.
    - **image**: The image file to be uploaded.
    """
    # Define the directory for the collection's images.
    # Each collection has its own folder in the "images" directory.
    images_dir = os.path.join("images/trainer", collection)
    os.makedirs(images_dir, exist_ok=True)

    # Save the uploaded image to the collection folder.
    file_path = os.path.join(images_dir, image.filename)
    try:
        with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        success = trainer.train(collection)
        if success:
            return {
                "status": 200,
                "message": "Images processed successfully",
                "collection_id": collection
            }
        else:
            # Processing failed, so raise an exception.
            raise Exception("Image processing failed")
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to save file: {e}"}, status_code=500)
    finally:
        image.file.close()

@app.get("/trainer", response_class=HTMLResponse)
async def trainer_page(request: Request):
    # Render the HTML page using the "index.html" template
    return templates.TemplateResponse("trainer.html", {"request": request})

@app.get("/trainer/images/{collection}", response_class=JSONResponse)
async def get_trainer_images(collection: str):
    """
    Retrieve a JSON list of all image URLs in the folder for the requested collection.
    The images are expected to be stored in the folder "images/trainer/{collection}" 
    and to have the file extension ".jps".
    
    Example response:
      {
         "images": [
            "/images/trainer/Rani/image1.jps",
            "/images/trainer/Rani/image2.jps"
         ]
      }
    """
    folder = os.path.join("images", "trainer", collection)
    if not os.path.exists(folder) or not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail="Collection folder not found")

    valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    try:
        files = os.listdir(folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing folder: {e}")

    # Filter files for the ".jps" extension (case-insensitive)
    images = [
        file for file in files
        if os.path.splitext(file)[1].lower() in valid_extensions
    ]

    # Build the URLs to access the images via the static mount
    image_urls = [f"/images/trainer/{collection}/{file}" for file in images]

    return {"images": image_urls}



@app.delete("/collection")
async def delete_collection(request: TrainRequest):
    # Here you can add your logic to process the images based on the collection_id and images_path
    try:
        utils.delete_rekognition_collection(collection_id=request.collection_id)
        return {
                "status": 200,
                "message": "Images processed successfully",
                "collection_id": request.collection_id
            }
    except Exception as e:
        logger.error(str(e))
        # Raise an HTTPException with status code 500 and include the error details.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats")
@cache(expire=60)
async def get_contacts():
    """
    Fetch data from an external API and return the JSON response.

    Returns:
        dict: A dictionary containing the JSON data from the external API.

    Raises:
        HTTPException: If the external API returns a non-200 status code.
    """
    # Use an asynchronous HTTP client to make the external GET request.
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.greenapi.com/waInstance{os.getenv('GREEN_API_INSTANCE')}/getContacts/{os.getenv('GREEN_API_TOKEN')}"
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors.
        except httpx.RequestError as exc:
            logger.error(str(exc))
            # This block handles network-related errors.
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting data: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            logger.error(str(exc))
            # This block handles responses with a non-success status code.
            raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch data from external API") from exc

    # Return the JSON content received from the external API.
    return response.json()    

@app.get("/contacts", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render the HTML page using the "index.html" template
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/collections", response_class=JSONResponse)
async def get_collections():
    kids = utils.config.get("kids", {})
    collection_ids = [
        kid_info.get("collection_id")
        for kid_info in kids.values()
        if kid_info.get("collection_id")  # ensure the field exists and is not empty
    ]
    return {"collections": collection_ids}

# Asynchronous wrapper to run the FastAPI server
async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=7020, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Asynchronous wrapper to run the WhatsApp bot in a thread.
# If bot.run_forever() is a blocking call, wrapping it with asyncio.to_thread
# allows it to run concurrently with the FastAPI server.
async def start_whatsapp_bot():
    await asyncio.to_thread(bot.run_forever)

# Main entry point to run both services concurrently
async def main():
    await asyncio.gather(
        start_fastapi(),
        start_whatsapp_bot()
    )

if __name__=="__main__":
    asyncio.run(main())
