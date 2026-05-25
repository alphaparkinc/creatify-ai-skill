import os
import sys
from creatify_ai import CreatifyClient, CreatifyError

def main():
    # 1. Initialize the Client using credentials from Environment variables (or direct strings)
    # Ensure you set these environment variables before running, e.g.:
    # Windows: set X_API_ID=your_id & set X_API_KEY=your_key
    # Unix: export X_API_ID="your_id" && export X_API_KEY="your_key"
    
    api_id = os.environ.get("X_API_ID", "your_api_id_here")
    api_key = os.environ.get("X_API_KEY", "your_api_key_here")
    
    if api_id == "your_api_id_here" or api_key == "your_api_key_here":
        print("[-] Please set your actual X_API_ID and X_API_KEY environment variables.")
        print("[-] Running with mock instructions...")
        # We will exit or show instructions
        sys.exit(0)
        
    print("[+] Initializing Creatify AI Client...")
    client = CreatifyClient(api_id=api_id, api_key=api_key)
    
    try:
        # 2. Check Credit Balance
        print("\n=== 1. Workspace Credit Balance ===")
        credits_info = client.get_remaining_credits()
        print(f"[+] Remaining Credits: {credits_info.get('credits', 'Unknown')}")
        
        # 3. Retrieve Available Avatars and Voices
        print("\n=== 2. Retrieve Avatars & Voices ===")
        avatars = client.get_available_avatars()
        voices = client.get_available_voices()
        
        print(f"[+] Retrieved {len(avatars)} standard avatars.")
        print(f"[+] Retrieved {len(voices)} voices.")
        
        if avatars:
            print(f"    Sample Avatar ID: {avatars[0].get('id')} ({avatars[0].get('name')})")
        if voices:
            print(f"    Sample Voice ID: {voices[0].get('id')} ({voices[0].get('name')})")
            
        # 4. URL-to-Video Workflow Demonstration
        print("\n=== 3. URL-to-Video Generation ===")
        product_url = "https://www.amazon.com/dp/B08P2H5LW2"  # Example product link
        print(f"[+] Scraping product URL: {product_url}")
        
        # Step A: Create link object
        link_obj = client.create_link(url=product_url)
        link_id = link_obj.get("id")
        print(f"[+] Link created successfully! Link ID: {link_id}")
        
        # Step B (Optional): Refine or update product details (e.g. title or style)
        # client.update_link(link_id, {"title": "Amazing Wireless Charger Pro"})
        
        # Step C: Start video generation job
        print("[+] Submitting video generation job (consumes credits)...")
        job_info = client.generate_video_from_link(
            link_id=link_id,
            visual_style="modern",
            aspect_ratio="9:16",
            language="en"
        )
        job_id = job_info.get("id")
        print(f"[+] Job submitted successfully! Job ID: {job_id}")
        
        # Step D: Poll until the video job is finished
        # (This takes about 3-5 minutes, let's mock-poll or wait)
        print("[*] Synchronous polling helper is available:")
        print(f"    video_data = client.poll_job(job_id='{job_id}', job_type='video')")
        
        # 5. Multi-Scene AI Avatar (Lipsync V2) Workflow Demonstration
        print("\n=== 4. Multi-Scene AI Avatar (Lipsync V2) ===")
        if len(avatars) > 0 and len(voices) > 0:
            avatar_id = avatars[0].get("id")
            voice_id = voices[0].get("id")
            
            # Setup scene config
            scenes = [
                {
                    "script": "Hello and welcome to this video! Today we're reviewing a premium product.",
                    "avatar_id": avatar_id,
                    "voice_id": voice_id,
                    "background_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800",
                    "caption_setting": {"style": "normal-black"}
                },
                {
                    "script": "It saves time, boosts productivity, and looks absolutely stunning. Get yours today!",
                    "avatar_id": avatar_id,
                    "voice_id": voice_id,
                    "background_url": "https://images.unsplash.com/photo-1618005198143-d528b96f2d8f?w=800"
                }
            ]
            
            print("[+] Submitting lipsync v2 avatar video job...")
            avatar_job = client.generate_lipsync_v2(
                scenes=scenes,
                aspect_ratio="9:16",
                model_version="aurora_v1_fast"
            )
            avatar_job_id = avatar_job.get("id")
            print(f"[+] Lipsync V2 Job ID: {avatar_job_id}")
            print("[*] You can poll this job using:")
            print(f"    result = client.poll_job(job_id='{avatar_job_id}', job_type='lipsync', version='v2')")
            
    except CreatifyError as e:
        print(f"[-] Encountered Creatify SDK Error: {e}")
    except Exception as e:
        print(f"[-] General Error: {e}")

if __name__ == "__main__":
    main()
