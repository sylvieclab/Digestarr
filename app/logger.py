"""
Centralized logging configuration with file rotation support
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List
from datetime import datetime

from app.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color codes for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[37m',     # White
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class LogManager:
    """Manages application logging with file rotation"""
    
    def __init__(self):
        self.log_dir = Path(settings.data_dir) / "logs"
        self.log_file = self.log_dir / "digestarr.log"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging with both console and file handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    def get_recent_logs(self, lines: int = 500) -> List[dict]:
        """
        Get recent log entries from the log file
        
        Args:
            lines: Number of recent log lines to return (default 500)
        
        Returns:
            List of log entry dictionaries with timestamp, level, logger, and message
        """
        if not self.log_file.exists():
            return []
        
        log_entries = []
        
        try:
            # Read last N lines from log file
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Read all lines and get last N
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Parse log lines
            for line in recent_lines:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse standard log format: timestamp - logger - level - message
                    parts = line.split(' - ', 3)
                    
                    if len(parts) >= 4:
                        log_entries.append({
                            'timestamp': parts[0],
                            'logger': parts[1],
                            'level': parts[2],
                            'message': parts[3]
                        })
                    else:
                        # Fallback for malformed lines
                        log_entries.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'logger': 'unknown',
                            'level': 'INFO',
                            'message': line
                        })
                except Exception:
                    # Skip malformed lines
                    continue
        
        except Exception as e:
            # Return error as log entry
            log_entries.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'logger': 'LogManager',
                'level': 'ERROR',
                'message': f'Failed to read log file: {str(e)}'
            })
        
        return log_entries
    
    def get_log_file_info(self) -> dict:
        """Get information about the log file"""
        if not self.log_file.exists():
            return {
                'exists': False,
                'size': 0,
                'modified': None
            }
        
        stat = self.log_file.stat()
        return {
            'exists': True,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }


# Global log manager instance
log_manager = LogManager()
