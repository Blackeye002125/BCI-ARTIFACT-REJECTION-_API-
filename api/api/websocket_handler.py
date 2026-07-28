"""
WebSocket Handler for Real-time Processing
"""

import asyncio
import json
import time
import numpy as np
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """
    Handles WebSocket connections for real-time EEG processing.
    """
    
    def __init__(self):
        """Initialize the WebSocket handler."""
        self.active_connections: List[WebSocket] = []
        self.processing_queue = asyncio.Queue()
        self.is_running = False
        self.processing_task = None
        
    async def start(self):
        """Start the WebSocket handler."""
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_queue())
        logger.info("WebSocket handler started")
    
    async def stop(self):
        """Stop the WebSocket handler."""
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info("WebSocket handler stopped")
    
    async def handle_connection(self, websocket: WebSocket):
        """
        Handle a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total: {len(self.active_connections)}")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                await self._process_message(websocket, data)
                
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def _process_message(self, websocket: WebSocket, message: str):
        """
        Process a received message.
        
        Args:
            websocket: WebSocket connection
            message: Received message
        """
        try:
            # Parse message
            data = json.loads(message)
            
            # Validate data
            if 'data' not in data:
                await websocket.send_json({
                    'error': 'Missing data field',
                    'timestamp': time.time()
                })
                return
            
            # Convert data to numpy array
            eeg_data = np.array(data['data'])
            
            # Process data
            start_time = time.perf_counter()
            cleaned_data = self._process_eeg_data(eeg_data)
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Send response
            response = {
                'cleaned_data': cleaned_data.tolist(),
                'processing_time_ms': processing_time,
                'timestamp': time.time()
            }
            
            await websocket.send_json(response)
            
        except json.JSONDecodeError:
            await websocket.send_json({
                'error': 'Invalid JSON format',
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Processing error: {e}")
            await websocket.send_json({
                'error': str(e),
                'timestamp': time.time()
            })
    
    def _process_eeg_data(self, data: np.ndarray) -> np.ndarray:
        """
        Process EEG data in real-time.
        
        Args:
            data: EEG data array
        
        Returns:
            Cleaned data
        """
        # Placeholder - actual processing logic
        # Apply simple filtering
        cleaned = data * 0.85  # Simulate artifact removal
        
        return cleaned
    
    async def _process_queue(self):
        """
        Process queued messages.
        """
        while self.is_running:
            try:
                # Get next message from queue
                websocket, message = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=1.0
                )
                
                # Process message
                await self._process_message(websocket, message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    def get_connection_count(self) -> int:
        """
        Get number of active connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
