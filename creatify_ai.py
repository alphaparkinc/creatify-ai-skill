import time
import logging
from typing import List, Dict, Any, Union, Optional
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CreatifyAI")

class CreatifyError(Exception):
    """Base exception class for Creatify AI SDK."""
    pass

class CreatifyAPIError(CreatifyError):
    """Exception raised when the API returns an error response."""
    def __init__(self, status_code: int, message: str, response_data: Any = None):
        super().__init__(f"API Error {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.response_data = response_data

class CreatifyAuthError(CreatifyError):
    """Exception raised for authentication failure (invalid X-API-ID or X-API-KEY)."""
    pass

class CreatifyCreditError(CreatifyError):
    """Exception raised when there are insufficient credits to perform the operation."""
    pass


class CreatifyClient:
    """
    Main SDK Client for interacting with the Creatify AI REST API.
    Provides complete programmatic access to video ad generation, AI avatars, text-to-speech, and more.
    """
    
    def __init__(self, api_id: str, api_key: str, base_url: str = "https://api.creatify.ai"):
        """
        Initialize the Creatify Client.
        
        Args:
            api_id (str): Your Creatify API ID.
            api_key (str): Your Creatify API Key.
            base_url (str, optional): The base URL for the Creatify API. Defaults to "https://api.creatify.ai".
        """
        if not api_id or not api_key:
            raise CreatifyAuthError("Both api_id and api_key must be provided.")
            
        self.api_id = api_id
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-ID": self.api_id,
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
        
    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Internal helper to execute HTTP requests with robust error handling."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.debug(f"Sending {method} request to {url}")
        
        try:
            response = self._session.request(method, url, **kwargs)
        except requests.RequestException as e:
            raise CreatifyError(f"HTTP Connection failure: {e}")
            
        # Specific error checking
        if response.status_code == 401 or response.status_code == 403:
            raise CreatifyAuthError("Invalid credentials. Please verify your X-API-ID and X-API-KEY.")
            
        # Parse JSON
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {"raw_content": response.text}
            
        if response.status_code == 400 and "credit" in response.text.lower():
            raise CreatifyCreditError(f"Insufficient credits: {response.text}")
            
        if not (200 <= response.status_code < 300):
            error_msg = data.get("detail") or data.get("message") or response.reason or response.text
            raise CreatifyAPIError(response.status_code, error_msg, response_data=data)
            
        return data

    # ==========================================
    # Workspace & Billing
    # ==========================================
    
    def get_remaining_credits(self) -> Dict[str, Any]:
        """
        Retrieve the remaining credit quota for the authenticated workspace.
        
        Returns:
            dict: Credits details (e.g., {'credits': 150}).
        """
        return self._request("GET", "/api/workspace/remainingcredits/")

    # ==========================================
    # URL-to-Video Workflow
    # ==========================================
    
    def create_link(self, url: str) -> Dict[str, Any]:
        """
        Convert a product/web URL into a Creatify Link object.
        
        Args:
            url (str): The product or website URL (e.g. Amazon or Shopify link).
            
        Returns:
            dict: The created Link object containing the 'id' (link_id) and scraped details.
        """
        payload = {"url": url}
        return self._request("POST", "/api/links/", json=payload)
        
    def get_link(self, link_id: str) -> Dict[str, Any]:
        """
        Retrieve details of an existing link object by ID.
        
        Args:
            link_id (str): The unique identifier of the Link.
            
        Returns:
            dict: Detailed link object with scraped text, image URLs, and title.
        """
        return self._request("GET", f"/api/links/{link_id}/")

    def update_link(self, link_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update or refine scraped assets/copy in the Link object before generating the video.
        
        Args:
            link_id (str): The unique identifier of the Link.
            params (dict): Fields to update (e.g., 'title', 'description', 'images', 'scripts').
            
        Returns:
            dict: The updated Link object.
        """
        return self._request("PUT", f"/api/links/{link_id}/", json=params)

    def generate_video_from_link(
        self, 
        link_id: str, 
        visual_style: str = "modern", 
        aspect_ratio: str = "9:16", 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Asynchronously create a video ad from a link ID.
        Consumes 5 credits for every 30 seconds.
        
        Args:
            link_id (str): The Link ID from create_link.
            visual_style (str, optional): Visual style configuration. Defaults to "modern".
            aspect_ratio (str, optional): Target video aspect ratio ("9:16", "16:9", "1:1"). Defaults to "9:16".
            language (str, optional): Voiceover/caption language (e.g. "en", "es"). Defaults to "en".
            
        Returns:
            dict: The video generation job details (contains the job 'id').
        """
        payload = {
            "link": link_id,
            "visual_style": visual_style,
            "aspect_ratio": aspect_ratio,
            "language": language
        }
        return self._request("POST", "/api/link_to_videos/", json=payload)

    def generate_preview_from_link(
        self, 
        link_id: str, 
        visual_style: str = "modern", 
        aspect_ratio: str = "9:16", 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a video preview from a link ID. 
        Previews are fast and cost 1 credit per 30 seconds instead of 5.
        
        Args:
            link_id (str): The Link ID.
            visual_style (str, optional): Visual style. Defaults to "modern".
            aspect_ratio (str, optional): Target aspect ratio. Defaults to "9:16".
            language (str, optional): Video language. Defaults to "en".
            
        Returns:
            dict: Preview job details.
        """
        payload = {
            "link": link_id,
            "visual_style": visual_style,
            "aspect_ratio": aspect_ratio,
            "language": language
        }
        return self._request("POST", "/api/link_to_videos/preview/", json=payload)

    def render_video_from_preview(self, preview_id: str) -> Dict[str, Any]:
        """
        Render the final video using an approved video preview ID.
        Costs 4 credits for every 30 seconds.
        
        Args:
            preview_id (str): The ID of the generated video preview.
            
        Returns:
            dict: Rendering job details.
        """
        payload = {"preview": preview_id}
        return self._request("POST", "/api/link_to_videos/render/", json=payload)

    def get_video_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation or rendering job.
        
        Args:
            job_id (str): The video job ID.
            
        Returns:
            dict: Current job details, including 'status' ("pending", "running", "done", "failed")
                  and 'video_output' URL when completed.
        """
        return self._request("GET", f"/api/link_to_videos/{job_id}/")

    # ==========================================
    # AI Avatars & Lipsync Workflow
    # ==========================================
    
    def get_available_avatars(self, paginated: bool = False, page: int = 1) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieve available standard and custom AI Avatars (Personas).
        
        Args:
            paginated (bool, optional): If True, returns a paginated structure. Defaults to False.
            page (int, optional): Page number when paginated is True. Defaults to 1.
            
        Returns:
            list or dict: List of available avatars, or a paginated object.
        """
        path = "/api/personas/paginated/" if paginated else "/api/personas/"
        params = {"page": page} if paginated else {}
        return self._request("GET", path, params=params)

    def get_avatar_by_id(self, avatar_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific AI Avatar by ID.
        
        Args:
            avatar_id (str): The unique identifier of the avatar.
            
        Returns:
            dict: Detailed avatar data.
        """
        return self._request("GET", f"/api/personas/{avatar_id}/")

    def get_available_voices(self, paginated: bool = False, page: int = 1) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieve a list of realistic AI voices available for voiceover and avatars.
        
        Args:
            paginated (bool, optional): If True, returns a paginated structure. Defaults to False.
            page (int, optional): Page number when paginated. Defaults to 1.
            
        Returns:
            list or dict: List of available voices, or a paginated object.
        """
        path = "/api/voices/paginated/" if paginated else "/api/voices/"
        params = {"page": page} if paginated else {}
        return self._request("GET", path, params=params)

    def generate_lipsync_v1(
        self, 
        text: str, 
        avatar_id: str, 
        aspect_ratio: str = "9:16", 
        model_version: str = "aurora_v1_fast"
    ) -> Dict[str, Any]:
        """
        Create a single-scene AI Avatar talking-head video from text (v1 API).
        Costs 5 credits per 30 seconds.
        
        Args:
            text (str): The speech script text.
            avatar_id (str): The unique identifier of the selected Avatar.
            aspect_ratio (str, optional): Target aspect ratio. Defaults to "9:16".
            model_version (str, optional): Generation AI model. Defaults to "aurora_v1_fast".
            
        Returns:
            dict: The job details.
        """
        payload = {
            "text": text,
            "creator": avatar_id,
            "aspect_ratio": aspect_ratio,
            "model_version": model_version
        }
        return self._request("POST", "/api/lipsyncs/", json=payload)

    def generate_lipsync_v2(
        self, 
        scenes: List[Dict[str, Any]], 
        aspect_ratio: str = "9:16", 
        model_version: str = "aurora_v1_fast"
    ) -> Dict[str, Any]:
        """
        Create a structured, multi-scene AI Avatar video (v2 API).
        Each scene can contain distinct scripts, avatars, voices, and backgrounds.
        Costs 5 credits per 30 seconds.
        
        Args:
            scenes (list): Array of dictionaries defining each scene:
                [
                    {
                        "script": "Script line for scene 1",
                        "avatar_id": "avatar-uuid-1",
                        "voice_id": "voice-uuid-1",
                        "background_url": "https://example.com/bg1.jpg",
                        "caption_setting": {"style": "normal-black"}
                    },
                    ...
                ]
            aspect_ratio (str, optional): Target aspect ratio. Defaults to "9:16".
            model_version (str, optional): Generation AI model. Defaults to "aurora_v1_fast".
            
        Returns:
            dict: The job details.
        """
        payload = {
            "scenes": scenes,
            "aspect_ratio": aspect_ratio,
            "model_version": model_version
        }
        return self._request("POST", "/api/lipsyncs_v2/", json=payload)

    def get_lipsync_job_status(self, job_id: str, version: str = "v2") -> Dict[str, Any]:
        """
        Check the status of a lipsync avatar generation job.
        
        Args:
            job_id (str): The lipsync job ID.
            version (str, optional): Either "v1" or "v2". Defaults to "v2".
            
        Returns:
            dict: Job details with 'status' and 'video_output' when finished.
        """
        endpoint = "/api/lipsyncs_v2/" if version == "v2" else "/api/lipsyncs/"
        return self._request("GET", f"{endpoint}{job_id}/")

    # ==========================================
    # Text-to-Speech Workflow
    # ==========================================
    
    def generate_speech(self, text: str, voice_id: str, accent: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate ultra-realistic text-to-speech audio.
        Costs 1 credit for every 30 seconds.
        
        Args:
            text (str): Speech transcription text.
            voice_id (str): ID of the voice to use.
            accent (str, optional): Localized voice accent. Defaults to None.
            
        Returns:
            dict: Audio details including the audio output URL.
        """
        payload = {
            "text": text,
            "voice": voice_id
        }
        if accent:
            payload["accent"] = accent
        return self._request("POST", "/api/text-to-speech/", json=payload)

    # ==========================================
    # Custom Templates Workflow
    # ==========================================
    
    def get_custom_templates(self) -> List[Dict[str, Any]]:
        """
        Retrieve available custom video templates in the workspace.
        
        Returns:
            list: List of templates with variable input specifications.
        """
        return self._request("GET", "/api/custom-templates/")

    def generate_video_from_template(self, template_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a video asynchronously by injecting custom text/assets into a template.
        Costs 5 credits per 30 seconds.
        
        Args:
            template_id (str): The unique identifier of the video template.
            variables (dict): Key-value pairs matching the variables defined in the template.
            
        Returns:
            dict: Job details.
        """
        payload = {
            "template": template_id,
            "variables": variables
        }
        return self._request("POST", "/api/custom_template_jobs/", json=payload)

    def get_template_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a custom template video rendering job.
        
        Args:
            job_id (str): The custom template job ID.
            
        Returns:
            dict: Job status details.
        """
        return self._request("GET", f"/api/custom_template_jobs/{job_id}/")

    # ==========================================
    # Unified Polling Helper
    # ==========================================
    
    def poll_job(
        self, 
        job_id: str, 
        job_type: str = "video", 
        version: str = "v2",
        interval_sec: int = 15, 
        timeout_sec: int = 600
    ) -> Dict[str, Any]:
        """
        Synchronously poll a running job until it completes or times out.
        
        Args:
            job_id (str): The ID of the job to poll.
            job_type (str, optional): The type of job: "video", "lipsync", "template", "speech". Defaults to "video".
            version (str, optional): API version for lipsync jobs ("v1" or "v2"). Defaults to "v2".
            interval_sec (int, optional): Polling interval in seconds. Defaults to 15.
            timeout_sec (int, optional): Max duration in seconds to wait before raising TimeoutError. Defaults to 600.
            
        Returns:
            dict: The completed job object containing 'video_output' (or 'audio_output') URL.
            
        Raises:
            TimeoutError: If the job takes longer than timeout_sec.
            CreatifyAPIError: If the job fails or encounters an API error.
        """
        start_time = time.time()
        logger.info(f"Started polling {job_type} job {job_id}...")
        
        while time.time() - start_time < timeout_sec:
            # Dispatch to appropriate status checker
            if job_type == "video":
                job = self.get_video_job_status(job_id)
            elif job_type == "lipsync":
                job = self.get_lipsync_job_status(job_id, version=version)
            elif job_type == "template":
                job = self.get_template_job_status(job_id)
            else:
                raise ValueError(f"Unknown job_type: {job_type}")
                
            status = job.get("status", "").lower()
            logger.info(f"Job {job_id} status: {status}")
            
            if status in ["done", "succeeded", "completed"]:
                logger.info(f"Job {job_id} completed successfully!")
                return job
            elif status in ["failed", "error"]:
                error_msg = job.get("error_message") or job.get("message") or "Unknown error"
                raise CreatifyAPIError(400, f"Job failed with status '{status}': {error_msg}", response_data=job)
                
            time.sleep(interval_sec)
            
        raise TimeoutError(f"Job {job_id} did not finish within {timeout_sec} seconds.")
