"""
Shell Tools - Safe shell command execution.
Provides controlled command execution with security measures.
"""

import subprocess
import shlex
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import os
import re


class ShellTools:
    """Shell command execution tools for the agent."""
    
    # Dangerous commands that should be blocked
    DANGEROUS_COMMANDS = [
        'rm -rf /', 'rm -rf /*', 'mkfs', 'dd if=/dev/zero',
        ':(){ :|:& };:', 'chmod -R 777 /', 'chown -R',
        '> /dev/sda', 'echo > /etc/', 'wget.*\\|.*sh',
        'curl.*\\|.*sh', 'sudo rm', 'pkill -9', 'killall',
    ]
    
    # Allowed command prefixes (whitelist approach)
    ALLOWED_PREFIXES = [
        'ls', 'dir', 'pwd', 'cd', 'cat', 'head', 'tail', 'wc',
        'grep', 'find', 'which', 'whereis', 'man', 'help',
        'echo', 'printf', 'date', 'time', 'uptime', 'whoami',
        'env', 'printenv', 'ps aux', 'top -b', 'free -m',
        'df -h', 'du -sh', 'uname', 'hostname', 'id',
        'mkdir', 'touch', 'cp', 'mv', 'ln', 'chmod', 'chown',
        'git ', 'python', 'python3', 'pip', 'pip3', 'npm', 'node',
        'docker ', 'kubectl ', 'ssh ', 'scp ', 'rsync ',
        'curl ', 'wget ', 'ping ', 'traceroute', 'netstat',
        'systemctl status', 'journalctl', 'tail -f',
    ]
    
    def __init__(self, allowed_dirs: Optional[List[str]] = None, 
                 timeout: int = 30):
        self.allowed_dirs = allowed_dirs or [os.getcwd()]
        self.timeout = timeout
        self.command_history: List[Dict[str, Any]] = []
    
    def _is_safe_command(self, command: str) -> Tuple[bool, str]:
        """Check if a command is safe to execute."""
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous command pattern detected: {pattern}"
        
        # Check if command starts with allowed prefix
        cmd_lower = command.lower().strip()
        for prefix in self.ALLOWED_PREFIXES:
            if cmd_lower.startswith(prefix.lower()):
                return True, "Command is whitelisted"
        
        # For unknown commands, check if they exist and are not dangerous
        try:
            cmd_parts = shlex.split(command)
            if cmd_parts:
                base_cmd = cmd_parts[0]
                # Check if command exists
                result = subprocess.run(
                    ['which', base_cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, f"Command not found: {base_cmd}"
                
                return True, "Command exists and passed basic checks"
        except Exception as e:
            return False, f"Error checking command: {str(e)}"
        
        return False, "Command not in whitelist"
    
    def _check_directory(self, path: str) -> bool:
        """Check if a path is within allowed directories."""
        try:
            abs_path = Path(path).resolve()
            for allowed_dir in self.allowed_dirs:
                allowed_abs = Path(allowed_dir).resolve()
                try:
                    abs_path.relative_to(allowed_abs)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def execute(self, command: str, cwd: Optional[str] = None,
               env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a shell command safely."""
        
        # Security checks
        is_safe, reason = self._is_safe_command(command)
        if not is_safe:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Security check failed: {reason}',
                'return_code': -1,
                'blocked': True,
            }
        
        # Check working directory
        if cwd and not self._check_directory(cwd):
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Working directory not allowed: {cwd}',
                'return_code': -1,
                'blocked': True,
            }
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=cwd,
                env=env or os.environ.copy(),
            )
            
            # Record in history
            self.command_history.append({
                'command': command,
                'cwd': cwd,
                'return_code': result.returncode,
                'output_length': len(result.stdout) + len(result.stderr),
            })
            
            # Limit output size
            max_output = 50000
            stdout = result.stdout[:max_output]
            stderr = result.stderr[:max_output]
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'return_code': result.returncode,
                'blocked': False,
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {self.timeout} seconds',
                'return_code': -1,
                'blocked': False,
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'return_code': -1,
                'blocked': False,
            }
    
    def execute_script(self, script: str, interpreter: str = "bash") -> Dict[str, Any]:
        """Execute a multi-line script."""
        # Create temporary script file
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=f'.{interpreter}',
                delete=False
            ) as f:
                f.write(script)
                script_path = f.name
            
            # Execute script
            command = f"{interpreter} {script_path}"
            result = self.execute(command)
            
            # Clean up
            os.unlink(script_path)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Script execution error: {str(e)}',
                'return_code': -1,
            }
    
    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return self.command_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear command history."""
        self.command_history = []
    
    def add_allowed_command(self, prefix: str) -> None:
        """Add a command prefix to the whitelist."""
        if prefix not in self.ALLOWED_PREFIXES:
            self.ALLOWED_PREFIXES.append(prefix)
    
    def add_allowed_directory(self, path: str) -> None:
        """Add a directory to the allowed list."""
        abs_path = Path(path).resolve()
        if abs_path not in [Path(p).resolve() for p in self.allowed_dirs]:
            self.allowed_dirs.append(str(abs_path))


# Global instance
_shell_tools: Optional[ShellTools] = None


def get_shell_tools(allowed_dirs: Optional[List[str]] = None,
                   timeout: int = 30) -> ShellTools:
    """Get or create the global shell tools instance."""
    global _shell_tools
    if _shell_tools is None:
        _shell_tools = ShellTools(allowed_dirs, timeout)
    return _shell_tools