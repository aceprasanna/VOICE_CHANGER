import os
import subprocess
import librosa
import soundfile as sf
from pydub import AudioSegment

def fix_mp3(input_mp3, output_mp3):
    """Fix corrupted MP3 using FFmpeg."""
    try:
        command = f'ffmpeg -y -i "{input_mp3}" -acodec libmp3lame -q:a 2 "{output_mp3}"'
        subprocess.run(command, shell=True, check=True)
        print(f"Fixed MP3 saved as: {output_mp3}")
        return output_mp3
    except subprocess.CalledProcessError as e:
        print(f"Error fixing MP3: {e}")
        return None

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using pydub."""
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        print(f"Converted {mp3_path} to {wav_path}")
        return wav_path
    except Exception as e:
        print(f"Error converting MP3 to WAV: {e}")
        return None

def change_voice(input_mp3, output_mp3, pitch_shift=4):
    """Modify the pitch of the voice and save as MP3."""
    fixed_mp3 = "male_voice_fixed.mp3"
    temp_wav = "temp.wav"
    
    # Step 1: Fix the MP3 if needed
    fixed_mp3 = fix_mp3(input_mp3, fixed_mp3)
    if not fixed_mp3:
        return
    
    # Step 2: Convert MP3 to WAV
    temp_wav = convert_mp3_to_wav(fixed_mp3, temp_wav)
    if not temp_wav:
        return
    
    # Step 3: Apply pitch shift
    try:
        y, sr = librosa.load(temp_wav, sr=None)
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
        
        # Save processed WAV
        processed_wav = "processed.wav"
        sf.write(processed_wav, y_shifted, sr)
        
        # Convert back to MP3
        processed_audio = AudioSegment.from_wav(processed_wav)
        processed_audio.export(output_mp3, format="mp3")
        
        print(f"Voice changed and saved as: {output_mp3}")
    
    except Exception as e:
        print(f"Error processing voice: {e}")
    
    # Step 4: Cleanup temporary files
    for file in [temp_wav, processed_wav, fixed_mp3]:
        if file and os.path.exists(file):
            os.remove(file)

# Example usage
change_voice("male_voice.mp3", "female_voice.mp3")

print("Processed voice saved as female_voice.mp3 ✅")
