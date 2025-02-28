# This script processes audio files in a specified directory, transcribes them using Azure's Speech Service, and saves the transcriptions to text files. It also moves processed audio files to a 'done' folder.
# https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-container-howto

import os
import shutil
import azure.cognitiveservices.speech as speechsdk

def process_audio_files():
    # Setup directories
    base_dir = os.path.dirname(__file__)
    input_folder = os.path.join(base_dir, "files")
    output_folder = "output"
    done_folder = "done"
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(done_folder, exist_ok=True)

    # Configure speech service
    try:
        # speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        speech_config = speechsdk.SpeechConfig(host="ws://localhost:5000")
        speech_config.speech_recognition_language="en-US"
    except Exception as e:
        print(f"Speech configuration error: {e}")
        return

    # Process each .wav file in the input folder
    for audio_file in os.listdir(input_folder):
        if not audio_file.endswith(".wav"):
            continue
            
        audio_path = os.path.join(input_folder, audio_file)
        output_path = os.path.join(output_folder, audio_file.replace(".wav", ".txt"))
        done_path = os.path.join(done_folder, audio_file)
        
        try:
            process_single_file(speech_config, audio_path, output_path, audio_file)
            # Move file only if processing succeeds
            shutil.move(audio_path, done_path)
            print(f"Moved {audio_file} to done folder")
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
            # Skip moving the file when there's an error

def process_single_file(speech_config, audio_path, output_path, filename):
    print(f"Processing file: {filename}")
    
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Use continuous recognition to get the full transcription
    done = False
    all_results = []
    
    # Define event handlers
    def recognized_cb(evt):
        all_results.append(evt.result.text)
        
    def stop_cb(evt):
        nonlocal done
        done = True
            
    # Connect event handlers
    recognizer.recognized.connect(recognized_cb)
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)
    
    # Start continuous recognition
    recognizer.start_continuous_recognition()
    
    # Wait for completion
    import time
    while not done:
        time.sleep(0.5)
    
    # Stop recognition
    recognizer.stop_continuous_recognition()
    
    if all_results:
        full_text = ' '.join(all_results)
        with open(output_path, "w") as output_file:
            output_file.write(full_text)
            print(full_text)
        print(f"Recognized and saved: {filename}")
        return True
    else:
        print(f"No speech could be recognized in file: {filename}")
        return False
if __name__ == "__main__":
    process_audio_files()