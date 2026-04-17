import os
import subprocess
import json
from typing import Dict, Any, Optional
from mutagen import File as MutagenFile
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from app.core.config import settings

class AudioService:
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extracts basic metadata using Mutagen."""
        audio = MutagenFile(file_path)
        if audio is None:
            return {}

        metadata = {
            "format": os.path.splitext(file_path)[1].lower().strip("."),
            "duration_ms": int(audio.info.length * 1000) if hasattr(audio.info, 'length') else 0,
            "size_bytes": os.path.getsize(file_path),
            "tags": {}
        }

        # Common tags extraction
        tags = {}
        if isinstance(audio, MP4):
            tags["title"] = audio.get("\xa9nam", [None])[0]
            tags["artist"] = audio.get("\xa9ART", [None])[0]
            tags["album"] = audio.get("\xa9alb", [None])[0]
            tags["composer"] = audio.get("\xa9wrt", [None])[0]
            tags["date"] = audio.get("\xa9day", [None])[0]
        elif isinstance(audio, FLAC):
            tags["title"] = audio.get("title", [None])[0]
            tags["artist"] = audio.get("artist", [None])[0]
            tags["album"] = audio.get("album", [None])[0]
            tags["composer"] = audio.get("composer", [None])[0]
            tags["date"] = audio.get("date", [None])[0]
        else:
            # Fallback for ID3 or others
            tags["title"] = audio.get("TIT2").text[0] if "TIT2" in audio else None
            tags["artist"] = audio.get("TPE1").text[0] if "TPE1" in audio else None
            tags["album"] = audio.get("TALB").text[0] if "TALB" in audio else None
            tags["composer"] = audio.get("TCOM").text[0] if "TCOM" in audio else None
            tags["date"] = audio.get("TDRC").text[0] if "TDRC" in audio else None

        metadata["tags"] = {k: v for k, v in tags.items() if v is not None}
        return metadata

    @staticmethod
    def get_stream_command(
        file_path: str, 
        start_ms: int = 0, 
        end_ms: Optional[int] = None, 
        target_format: str = "flac"
    ) -> list:
        """
        Generates an FFmpeg command to stream a portion of an audio file.
        ALAC/APE will be converted to FLAC.
        """
        cmd = ["ffmpeg", "-ss", str(start_ms / 1000.0)]
        
        if end_ms:
            duration_sec = (end_ms - start_ms) / 1000.0
            cmd.extend(["-t", str(duration_sec)])
            
        cmd.extend(["-i", file_path])
        
        if target_format == "flac":
            cmd.extend(["-f", "flac", "-"])
        elif target_format == "mp3":
            cmd.extend(["-f", "mp3", "-"])
        else:
            # Default to original if not specified, but usually we want flac for lossless
            cmd.extend(["-f", "flac", "-"])
            
        return cmd

audio_service = AudioService()
