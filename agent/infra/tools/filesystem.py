"""
Filesystem Tools - File and directory operations.
Provides safe file access for the agent.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


class FilesystemTools:
    """Filesystem manipulation tools for the agent."""
    
    def __init__(self, base_dir: str = "./data/agent/workspace"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _safe_path(self, path: str) -> Path:
        """Ensure path is within base directory (security)."""
        full_path = (self.base_dir / path).resolve()
        
        # Prevent path traversal attacks
        try:
            full_path.relative_to(self.base_dir)
            return full_path
        except ValueError:
            raise ValueError(f"Path '{path}' is outside allowed directory")
    
    def read_file(self, path: str, max_size: int = 100000) -> Optional[str]:
        """Read contents of a file."""
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return None
            
            if not safe_path.is_file():
                return None
            
            # Check file size
            file_size = safe_path.stat().st_size
            if file_size > max_size:
                return f"[File too large: {file_size} bytes. Max allowed: {max_size} bytes]"
            
            with open(safe_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read(max_size)
                
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file."""
        try:
            safe_path = self._safe_path(path)
            
            # Create parent directories if needed
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            return False
    
    def append_file(self, path: str, content: str) -> bool:
        """Append content to a file."""
        try:
            safe_path = self._safe_path(path)
            
            with open(safe_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            return False
    
    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        try:
            safe_path = self._safe_path(path)
            
            if safe_path.exists() and safe_path.is_file():
                safe_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def list_directory(self, path: str = ".") -> Optional[List[Dict[str, Any]]]:
        """List contents of a directory."""
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists() or not safe_path.is_dir():
                return None
            
            items = []
            for item in safe_path.iterdir():
                try:
                    stat = item.stat()
                    items.append({
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else 0,
                        'modified': stat.st_mtime,
                    })
                except:
                    continue
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (x['type'] != 'directory', x['name']))
            
            return items
            
        except Exception as e:
            return None
    
    def create_directory(self, path: str) -> bool:
        """Create a directory."""
        try:
            safe_path = self._safe_path(path)
            safe_path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False
    
    def delete_directory(self, path: str) -> bool:
        """Delete a directory and its contents."""
        try:
            safe_path = self._safe_path(path)
            
            if safe_path.exists() and safe_path.is_dir():
                shutil.rmtree(safe_path)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """Move or rename a file."""
        try:
            safe_src = self._safe_path(src)
            safe_dst = self._safe_path(dst)
            
            if safe_src.exists():
                shutil.move(str(safe_src), str(safe_dst))
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def copy_file(self, src: str, dst: str) -> bool:
        """Copy a file."""
        try:
            safe_src = self._safe_path(src)
            safe_dst = self._safe_path(dst)
            
            if safe_src.exists() and safe_src.is_file():
                safe_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(safe_src), str(safe_dst))
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        try:
            safe_path = self._safe_path(path)
            return safe_path.exists() and safe_path.is_file()
        except:
            return False
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return None
            
            stat = safe_path.stat()
            
            return {
                'name': safe_path.name,
                'path': str(safe_path.relative_to(self.base_dir)),
                'type': 'directory' if safe_path.is_dir() else 'file',
                'size': stat.st_size if safe_path.is_file() else 0,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
            }
            
        except Exception as e:
            return None
    
    def search_files(self, pattern: str = "*", recursive: bool = False) -> List[str]:
        """Search for files matching a pattern."""
        try:
            if recursive:
                matches = list(self.base_dir.rglob(pattern))
            else:
                matches = list(self.base_dir.glob(pattern))
            
            return [
                str(m.relative_to(self.base_dir))
                for m in matches
                if m.is_file()
            ]
            
        except:
            return []


# Global instance
_fs_tools: Optional[FilesystemTools] = None


def get_filesystem_tools(base_dir: str = "./data/agent/workspace") -> FilesystemTools:
    """Get or create the global filesystem tools instance."""
    global _fs_tools
    if _fs_tools is None:
        _fs_tools = FilesystemTools(base_dir)
    return _fs_tools