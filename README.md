# creatify-ai-skill

> **GenPark AI Agent Skill** -- # Creatify AI Skill - Python SDK & Developer Integration Guide

This repository contains the **Creatify AI Developer Skill** — a comprehensive Python client SDK wrapper and developer documentation designed to automate the generation of high-impact video ads, AI avatars, text-to-speech, and asset generation using the official **Creatify AI REST API** (v1 and v2).

---

## 🚀 Product Capabilities & Overview

**Creatify AI** is an advanced AI-powered marketing asset platform that automates the end-to-end creation of video ads. Key technical features include:

*   **URL-to-Video API**: Automatically parses any product link (Shopify, Amazon, Etsy, etc.), extracts visual assets, writes compelling marketing scripts, synthesizes voiceovers, and generates high-converting short-form videos.
*   **AI Avatars & Lipsync (v1 & v2)**: Converts text or audio files into lifelike talking-head videos featuring highly realistic avatars.
    *   *v1*: Simple single-segment actor with a single voice and script.
    *   *v2*: Multi-scene narrative configuration allowing scene-by-scene editing of actors, voices, backgrounds, and caption styling.
*   **Text-to-Speech (TTS) & Voice Cloning**: Converts text into ultra-realistic spoken audio in multiple accents or clones specific voices.
*   **Custom Templates**: Enables mass-personalization by programmatically injecting dynamic content into pre-made video templates.
*   **Aurora (Single-Image Talking Head)**: Converts a single face photo and voice clip into an expressive talking-head video.
*   **IAB Banner Images**: Instantly generates IAB-compliant ad banners in multiple standardized sizes from a single product image.

---

## 💳 Credit Usage & Cost Matrix

Creatify AI operates on a subscription-based credit system. API-based calls consume credits as follows:

| Endpoint Feature | Credit Cost | Description |
| :--- | :--- | :--- |
| **Script Generation** | `1 credit` | Generates ad copy/scripts from a title or description. |
| **Product Image Preview** | `1 credit` | Generates a preview image for a product. |
| **Video Preview (URL/Avatar)** | `1 credit` | 30s quick video preview (fast, cost-effective). |
| **Video Rendering (URL/Avatar)** | `4 credits` | 30s final high-resolution video render. |
| **Full Video Generation (Direct)** | `5 credits` | 30s video created directly without preview steps. |
| **Text-to-Speech** | `1 credit` | Generates 30s of high-quality speech audio. |
| **IAB Banner Images** | `2 credits` | Generates multi-size banner ads from one image. |

---

## 🛠️ Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/creatify-ai-skill.git
   cd creatify-ai-skill
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Obtain your API Credentials from the Creatify Dashboard (Workspace Settings -> API Settings) and set them as environment variables:
   *   **Windows (CMD/PowerShell)**:
       ```powershell
       $env:X_API_ID="your_api_id"
       $env:X_API_KEY="your_api_key"
       ```
   *   **Linux/macOS**:
       ```bash
       export X_API_ID="your_api_id"
       export X_API_KEY="your_api_key"
       ```

---

## 💻 SDK Usage Reference

The `creatify_ai.py` client SDK wraps the REST endpoints cleanly. Here are the core code snippets:

### 1. Initialize Client & Check Balance
```python
from creatify_ai import CreatifyClient

client = CreatifyClient(api_id="your_api_id", api_key="your_api_key")

# Check remaining credits
info = client.get_remaining_credits()
print(f"Remaining credits: {info['credits']}")
```

### 2. URL-to-Video Generation Workflow
The typical API workflow is asynchronous:
```python
# Step 1: Create a link object from product page URL
link_obj = client.create_link("https://www.amazon.com/dp/B08P2H5LW2")
link_id = link_obj["id"]

# Step 2: Trigger Async Video Generation
job = client.generate_video_from_link(
    link_id=link_id,
    visual_style="modern",
    aspect_ratio="9:16",
    language="en"
)
job_id = job["id"]

# Step 3: Poll for final output MP4 (with built-in polling helper)
result = client.poll_job(job_id=job_id, job_type="video")
print(f"Finished Video URL: {result['video_output']}")
```

### 3. Multi-Scene AI Avatar (Lipsync V2) Workflow
Structure your video scene-by-scene with custom scripts, voices, backgrounds, and actors:
```python
scenes = [
    {
        "script": "Introducing our brand new marketing skill wrapper!",
        "avatar_id": "avatar-uuid-1",
        "voice_id": "voice-uuid-1",
        "background_url": "https://example.com/bg1.jpg",
        "caption_setting": {"style": "normal-black"}
    },
    {
        "script": "It allows developers and AIs to automate video generation instantly.",
        "avatar_id": "avatar-uuid-1",
        "voice_id": "voice-uuid-1",
        "background_url": "https://example.com/bg2.jpg"
    }
]

# Generate lipsync v2 video job
job = client.generate_lipsync_v2(scenes=scenes, aspect_ratio="9:16")
job_id = job["id"]

# Poll for completed video URL
result = client.poll_job(job_id=job_id, job_type="lipsync", version="v2")
print(f"AI Avatar Video URL: {result['video_output']}")
```

---

## 🔬 API Endpoint Specifications

All endpoints use `https://api.creatify.ai` as their base URL and require `X-API-ID` and `X-API-KEY` headers.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/workspace/remainingcredits/` | Get current credit balance. |
| **POST** | `/api/links/` | Scrapes a webpage and creates a link resource. |
| **PUT** | `/api/links/{id}/` | Refines and updates link text/image assets. |
| **POST** | `/api/link_to_videos/` | Triggers a 5-credit video generation job. |
| **POST** | `/api/link_to_videos/preview/` | Triggers a fast 1-credit preview video. |
| **POST** | `/api/link_to_videos/render/` | Renders a final video using preview ID. |
| **GET** | `/api/link_to_videos/{id}/` | Polls status of a video job. |
| **GET** | `/api/personas/` | Gets list of available AI avatar actors. |
| **GET** | `/api/voices/` | Gets list of all available voices. |
| **POST** | `/api/lipsyncs/` | Generates simple 1-scene avatar video (v1). |
| **POST** | `/api/lipsyncs_v2/` | Generates complex multi-scene avatar video (v2). |
| **GET** | `/api/lipsyncs_v2/{id}/` | Polls status of a lipsync v2 job. |
| **POST** | `/api/text-to-speech/` | Synthesizes text into high-quality audio file. |

---

## 📜 License
This project is licensed under the MIT License.