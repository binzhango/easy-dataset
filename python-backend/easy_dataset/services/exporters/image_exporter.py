"""Image dataset exporter."""

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from easy_dataset.models.image_dataset import ImageDatasets
from easy_dataset.services.image_service import ImageService

logger = logging.getLogger(__name__)


class ImageDatasetExporter:
    """
    Exporter for image datasets.
    
    Features:
    - Export with image paths or base64 data
    - Support multiple export formats (JSON, JSONL, custom)
    - Handle large image datasets efficiently
    - Include metadata and annotations
    """
    
    def __init__(
        self,
        db_session: Session,
        image_service: ImageService
    ):
        """
        Initialize image dataset exporter.
        
        Args:
            db_session: Database session
            image_service: Image service for loading images
        """
        self.db = db_session
        self.image_service = image_service
    
    def format_entry_with_path(
        self,
        entry: ImageDatasets,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Format dataset entry with image path.
        
        Args:
            entry: ImageDatasets instance
            include_metadata: Whether to include metadata
            
        Returns:
            Dictionary with entry data
        """
        # Get image
        image = self.image_service.get_image(entry.image_id)
        
        data = {
            "image_path": image.path if image else "",
            "image_name": entry.image_name,
            "question": entry.question,
            "answer": entry.answer,
            "answer_type": entry.answer_type
        }
        
        if include_metadata:
            data.update({
                "id": entry.id,
                "model": entry.model,
                "confirmed": entry.confirmed,
                "score": entry.score,
                "tags": entry.tags,
                "note": entry.note,
                "created_at": entry.create_at.isoformat(),
                "updated_at": entry.update_at.isoformat()
            })
            
            if image:
                data["image_metadata"] = {
                    "width": image.width,
                    "height": image.height,
                    "size": image.size
                }
        
        return data
    
    def format_entry_with_base64(
        self,
        entry: ImageDatasets,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Format dataset entry with base64 encoded image.
        
        Args:
            entry: ImageDatasets instance
            include_metadata: Whether to include metadata
            
        Returns:
            Dictionary with entry data
        """
        # Get base64 image data
        image_data_url = self.image_service.get_image_data_url(entry.image_id)
        
        data = {
            "image": image_data_url or "",
            "image_name": entry.image_name,
            "question": entry.question,
            "answer": entry.answer,
            "answer_type": entry.answer_type
        }
        
        if include_metadata:
            image = self.image_service.get_image(entry.image_id)
            
            data.update({
                "id": entry.id,
                "model": entry.model,
                "confirmed": entry.confirmed,
                "score": entry.score,
                "tags": entry.tags,
                "note": entry.note,
                "created_at": entry.create_at.isoformat(),
                "updated_at": entry.update_at.isoformat()
            })
            
            if image:
                data["image_metadata"] = {
                    "width": image.width,
                    "height": image.height,
                    "size": image.size
                }
        
        return data
    
    def format_entry_llava_style(
        self,
        entry: ImageDatasets,
        use_base64: bool = False
    ) -> Dict[str, Any]:
        """
        Format entry in LLaVA training format.
        
        Args:
            entry: ImageDatasets instance
            use_base64: Whether to use base64 or path
            
        Returns:
            Dictionary in LLaVA format
        """
        if use_base64:
            image_ref = self.image_service.get_image_data_url(entry.image_id) or ""
        else:
            image = self.image_service.get_image(entry.image_id)
            image_ref = image.path if image else ""
        
        return {
            "id": entry.id,
            "image": image_ref,
            "conversations": [
                {
                    "from": "human",
                    "value": f"<image>\n{entry.question}"
                },
                {
                    "from": "gpt",
                    "value": entry.answer
                }
            ]
        }
    
    def format_entry_vqa_style(
        self,
        entry: ImageDatasets,
        use_base64: bool = False
    ) -> Dict[str, Any]:
        """
        Format entry in VQA (Visual Question Answering) format.
        
        Args:
            entry: ImageDatasets instance
            use_base64: Whether to use base64 or path
            
        Returns:
            Dictionary in VQA format
        """
        if use_base64:
            image_ref = self.image_service.get_image_data_url(entry.image_id) or ""
        else:
            image = self.image_service.get_image(entry.image_id)
            image_ref = image.path if image else ""
        
        return {
            "question_id": entry.id,
            "image_id": entry.image_id,
            "image": image_ref,
            "question": entry.question,
            "answer": entry.answer,
            "answer_type": entry.answer_type
        }
    
    def export_json(
        self,
        entries: List[ImageDatasets],
        output_path: str,
        use_base64: bool = False,
        format_style: str = "default",
        include_metadata: bool = True
    ) -> int:
        """
        Export image dataset to JSON file.
        
        Args:
            entries: List of ImageDatasets instances
            output_path: Output file path
            use_base64: Whether to include base64 image data
            format_style: Format style (default, llava, vqa)
            include_metadata: Whether to include metadata
            
        Returns:
            Number of entries exported
        """
        formatted_entries = []
        
        for entry in entries:
            if format_style == "llava":
                formatted = self.format_entry_llava_style(entry, use_base64)
            elif format_style == "vqa":
                formatted = self.format_entry_vqa_style(entry, use_base64)
            else:
                if use_base64:
                    formatted = self.format_entry_with_base64(entry, include_metadata)
                else:
                    formatted = self.format_entry_with_path(entry, include_metadata)
            
            formatted_entries.append(formatted)
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted_entries, f, indent=2, ensure_ascii=False)
        
        logger.info(
            f"Exported {len(formatted_entries)} image dataset entries to {output_path} "
            f"(format: {format_style}, base64: {use_base64})"
        )
        
        return len(formatted_entries)
    
    def export_jsonl(
        self,
        entries: List[ImageDatasets],
        output_path: str,
        use_base64: bool = False,
        format_style: str = "default",
        include_metadata: bool = True
    ) -> int:
        """
        Export image dataset to JSONL file.
        
        Args:
            entries: List of ImageDatasets instances
            output_path: Output file path
            use_base64: Whether to include base64 image data
            format_style: Format style (default, llava, vqa)
            include_metadata: Whether to include metadata
            
        Returns:
            Number of entries exported
        """
        count = 0
        
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                if format_style == "llava":
                    formatted = self.format_entry_llava_style(entry, use_base64)
                elif format_style == "vqa":
                    formatted = self.format_entry_vqa_style(entry, use_base64)
                else:
                    if use_base64:
                        formatted = self.format_entry_with_base64(entry, include_metadata)
                    else:
                        formatted = self.format_entry_with_path(entry, include_metadata)
                
                f.write(json.dumps(formatted, ensure_ascii=False) + "\n")
                count += 1
        
        logger.info(
            f"Exported {count} image dataset entries to {output_path} "
            f"(format: {format_style}, base64: {use_base64})"
        )
        
        return count
    
    def export_with_images(
        self,
        entries: List[ImageDatasets],
        output_dir: str,
        format_style: str = "default",
        copy_images: bool = True
    ) -> Dict[str, Any]:
        """
        Export dataset with separate image files.
        
        Args:
            entries: List of ImageDatasets instances
            output_dir: Output directory path
            format_style: Format style for metadata
            copy_images: Whether to copy image files
            
        Returns:
            Dictionary with export results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create images subdirectory
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Export metadata
        metadata_entries = []
        copied_images = 0
        
        for entry in entries:
            image = self.image_service.get_image(entry.image_id)
            
            if not image:
                logger.warning(f"Image not found for entry {entry.id}")
                continue
            
            # Copy image file if requested
            if copy_images:
                image_data = self.image_service.get_image_data(entry.image_id)
                
                if image_data:
                    # Save to images directory
                    image_filename = f"{entry.image_id}_{image.image_name}"
                    image_path = images_dir / image_filename
                    
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    
                    copied_images += 1
                    relative_image_path = f"images/{image_filename}"
                else:
                    relative_image_path = image.path
            else:
                relative_image_path = image.path
            
            # Format metadata
            if format_style == "llava":
                formatted = self.format_entry_llava_style(entry, use_base64=False)
                formatted["image"] = relative_image_path
            elif format_style == "vqa":
                formatted = self.format_entry_vqa_style(entry, use_base64=False)
                formatted["image"] = relative_image_path
            else:
                formatted = self.format_entry_with_path(entry, include_metadata=True)
                formatted["image_path"] = relative_image_path
            
            metadata_entries.append(formatted)
        
        # Write metadata file
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_entries, f, indent=2, ensure_ascii=False)
        
        # Write README
        readme_path = output_path / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"Image Dataset Export\n")
            f.write(f"====================\n\n")
            f.write(f"Total entries: {len(metadata_entries)}\n")
            f.write(f"Images copied: {copied_images}\n")
            f.write(f"Format style: {format_style}\n\n")
            f.write(f"Files:\n")
            f.write(f"- metadata.json: Dataset metadata and annotations\n")
            f.write(f"- images/: Image files\n")
        
        logger.info(
            f"Exported {len(metadata_entries)} entries with {copied_images} images "
            f"to {output_dir}"
        )
        
        return {
            "total_entries": len(metadata_entries),
            "images_copied": copied_images,
            "output_dir": str(output_path),
            "metadata_file": str(metadata_path),
            "images_dir": str(images_dir)
        }
    
    def export_huggingface_format(
        self,
        entries: List[ImageDatasets],
        output_dir: str,
        dataset_name: str = "image_dataset",
        copy_images: bool = True
    ) -> Dict[str, Any]:
        """
        Export in Hugging Face datasets format.
        
        Args:
            entries: List of ImageDatasets instances
            output_dir: Output directory path
            dataset_name: Dataset name
            copy_images: Whether to copy images
            
        Returns:
            Dictionary with export results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create images directory
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Prepare data
        data_entries = []
        
        for entry in entries:
            image = self.image_service.get_image(entry.image_id)
            
            if not image:
                continue
            
            # Copy image
            if copy_images:
                image_data = self.image_service.get_image_data(entry.image_id)
                
                if image_data:
                    image_filename = f"{entry.image_id}_{image.image_name}"
                    image_path = images_dir / image_filename
                    
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    
                    relative_path = f"images/{image_filename}"
                else:
                    relative_path = image.path
            else:
                relative_path = image.path
            
            # Format entry
            data_entries.append({
                "image": relative_path,
                "question": entry.question,
                "answer": entry.answer,
                "answer_type": entry.answer_type,
                "metadata": {
                    "model": entry.model,
                    "score": entry.score,
                    "confirmed": entry.confirmed,
                    "tags": entry.tags
                }
            })
        
        # Write data file
        data_path = output_path / "data.jsonl"
        with open(data_path, "w", encoding="utf-8") as f:
            for entry in data_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # Write dataset_info.json
        dataset_info = {
            "dataset_name": dataset_name,
            "description": "Image question-answering dataset",
            "version": "1.0.0",
            "features": {
                "image": {"dtype": "string"},
                "question": {"dtype": "string"},
                "answer": {"dtype": "string"},
                "answer_type": {"dtype": "string"},
                "metadata": {"dtype": "dict"}
            },
            "splits": {
                "train": {
                    "num_examples": len(data_entries)
                }
            }
        }
        
        info_path = output_path / "dataset_info.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(dataset_info, f, indent=2)
        
        logger.info(
            f"Exported {len(data_entries)} entries in Hugging Face format to {output_dir}"
        )
        
        return {
            "total_entries": len(data_entries),
            "output_dir": str(output_path),
            "data_file": str(data_path),
            "info_file": str(info_path)
        }
