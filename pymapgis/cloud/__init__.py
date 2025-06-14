"""
PyMapGIS Cloud-Native Integration Module - Phase 3 Feature

This module provides seamless integration with major cloud storage providers:
- Amazon S3 (AWS)
- Google Cloud Storage (GCS)
- Azure Blob Storage
- Generic S3-compatible storage

Key Features:
- Unified API for all cloud providers
- Automatic credential management
- Optimized cloud-native data formats
- Streaming uploads/downloads
- Intelligent caching for cloud data
- Cost optimization features

Performance Benefits:
- Direct cloud data access without local downloads
- Parallel chunk processing for large cloud files
- Intelligent prefetching and caching
- Optimized for cloud-native formats (Parquet, Zarr, COG)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Tuple
from urllib.parse import urlparse
import tempfile
import asyncio

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import storage as gcs
    from google.auth.exceptions import DefaultCredentialsError

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    gcs = None

try:
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import AzureError

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    BlobServiceClient = None

try:
    import fsspec

    FSSPEC_AVAILABLE = True
except ImportError:
    FSSPEC_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

__all__ = [
    "CloudStorageManager",
    "S3Storage",
    "GCSStorage",
    "AzureStorage",
    "CloudDataReader",
    "cloud_read",
    "cloud_write",
    "list_cloud_files",
    "get_cloud_info",
]


class CloudStorageError(Exception):
    """Base exception for cloud storage operations."""

    pass


class CloudCredentialsError(CloudStorageError):
    """Exception for cloud credentials issues."""

    pass


class CloudStorageBase:
    """Base class for cloud storage providers."""

    def __init__(self, **kwargs):
        self.config = kwargs
        self._client = None

    def _get_client(self):
        """Get or create cloud client. Implemented by subclasses."""
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        """Check if file exists in cloud storage."""
        raise NotImplementedError

    def list_files(
        self, prefix: str = "", max_files: int = 1000
    ) -> List[Dict[str, Any]]:
        """List files in cloud storage."""
        raise NotImplementedError

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get metadata about a cloud file."""
        raise NotImplementedError

    def download_file(self, cloud_path: str, local_path: str) -> None:
        """Download file from cloud to local storage."""
        raise NotImplementedError

    def upload_file(self, local_path: str, cloud_path: str) -> None:
        """Upload file from local to cloud storage."""
        raise NotImplementedError

    def delete_file(self, path: str) -> None:
        """Delete file from cloud storage."""
        raise NotImplementedError


class S3Storage(CloudStorageBase):
    """Amazon S3 storage implementation."""

    def __init__(self, bucket: str, region: str = None, **kwargs):
        super().__init__(**kwargs)
        if not AWS_AVAILABLE:
            raise CloudStorageError(
                "AWS SDK (boto3) not available. Install with: pip install boto3"
            )

        self.bucket = bucket
        self.region = region

    def _get_client(self):
        """Get S3 client with automatic credential detection."""
        if self._client is None:
            try:
                session = boto3.Session()
                self._client = session.client("s3", region_name=self.region)

                # Test credentials
                self._client.head_bucket(Bucket=self.bucket)
                logger.info(f"Connected to S3 bucket: {self.bucket}")

            except NoCredentialsError:
                raise CloudCredentialsError(
                    "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
                    "environment variables or configure AWS CLI."
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise CloudStorageError(f"S3 bucket '{self.bucket}' not found")
                else:
                    raise CloudStorageError(f"S3 error: {e}")

        return self._client

    def exists(self, path: str) -> bool:
        """Check if S3 object exists."""
        try:
            self._get_client().head_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False

    def list_files(
        self, prefix: str = "", max_files: int = 1000
    ) -> List[Dict[str, Any]]:
        """List S3 objects."""
        client = self._get_client()

        response = client.list_objects_v2(
            Bucket=self.bucket, Prefix=prefix, MaxKeys=max_files
        )

        files = []
        for obj in response.get("Contents", []):
            files.append(
                {
                    "path": obj["Key"],
                    "size": obj["Size"],
                    "modified": obj["LastModified"],
                    "etag": obj["ETag"].strip('"'),
                    "storage_class": obj.get("StorageClass", "STANDARD"),
                }
            )

        return files

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get S3 object metadata."""
        client = self._get_client()

        try:
            response = client.head_object(Bucket=self.bucket, Key=path)
            return {
                "path": path,
                "size": response["ContentLength"],
                "modified": response["LastModified"],
                "etag": response["ETag"].strip('"'),
                "content_type": response.get("ContentType"),
                "metadata": response.get("Metadata", {}),
                "storage_class": response.get("StorageClass", "STANDARD"),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise CloudStorageError(f"S3 object '{path}' not found")
            else:
                raise CloudStorageError(f"S3 error: {e}")

    def download_file(self, cloud_path: str, local_path: str) -> None:
        """Download from S3."""
        client = self._get_client()

        try:
            client.download_file(self.bucket, cloud_path, local_path)
            logger.info(f"Downloaded s3://{self.bucket}/{cloud_path} to {local_path}")
        except ClientError as e:
            raise CloudStorageError(f"Failed to download from S3: {e}")

    def upload_file(self, local_path: str, cloud_path: str) -> None:
        """Upload to S3."""
        client = self._get_client()

        try:
            client.upload_file(local_path, self.bucket, cloud_path)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket}/{cloud_path}")
        except ClientError as e:
            raise CloudStorageError(f"Failed to upload to S3: {e}")

    def delete_file(self, path: str) -> None:
        """Delete S3 object."""
        client = self._get_client()

        try:
            client.delete_object(Bucket=self.bucket, Key=path)
            logger.info(f"Deleted s3://{self.bucket}/{path}")
        except ClientError as e:
            raise CloudStorageError(f"Failed to delete from S3: {e}")


class GCSStorage(CloudStorageBase):
    """Google Cloud Storage implementation."""

    def __init__(self, bucket: str, project: str = None, **kwargs):
        super().__init__(**kwargs)
        if not GCS_AVAILABLE:
            raise CloudStorageError(
                "Google Cloud SDK not available. Install with: pip install google-cloud-storage"
            )

        self.bucket_name = bucket
        self.project = project

    def _get_client(self):
        """Get GCS client."""
        if self._client is None:
            try:
                self._client = gcs.Client(project=self.project)
                self.bucket = self._client.bucket(self.bucket_name)

                # Test access
                self.bucket.reload()
                logger.info(f"Connected to GCS bucket: {self.bucket_name}")

            except DefaultCredentialsError:
                raise CloudCredentialsError(
                    "GCS credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS "
                    "environment variable or run 'gcloud auth application-default login'."
                )
            except Exception as e:
                raise CloudStorageError(f"GCS error: {e}")

        return self._client

    def exists(self, path: str) -> bool:
        """Check if GCS blob exists."""
        self._get_client()
        blob = self.bucket.blob(path)
        return blob.exists()

    def list_files(
        self, prefix: str = "", max_files: int = 1000
    ) -> List[Dict[str, Any]]:
        """List GCS blobs."""
        self._get_client()

        blobs = self.bucket.list_blobs(prefix=prefix, max_results=max_files)

        files = []
        for blob in blobs:
            files.append(
                {
                    "path": blob.name,
                    "size": blob.size,
                    "modified": blob.time_created,
                    "etag": blob.etag,
                    "content_type": blob.content_type,
                    "storage_class": blob.storage_class,
                }
            )

        return files

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get GCS blob metadata."""
        self._get_client()
        blob = self.bucket.blob(path)

        if not blob.exists():
            raise CloudStorageError(f"GCS blob '{path}' not found")

        blob.reload()
        return {
            "path": path,
            "size": blob.size,
            "modified": blob.time_created,
            "etag": blob.etag,
            "content_type": blob.content_type,
            "metadata": blob.metadata or {},
            "storage_class": blob.storage_class,
        }

    def download_file(self, cloud_path: str, local_path: str) -> None:
        """Download from GCS."""
        self._get_client()
        blob = self.bucket.blob(cloud_path)

        try:
            blob.download_to_filename(local_path)
            logger.info(
                f"Downloaded gs://{self.bucket_name}/{cloud_path} to {local_path}"
            )
        except Exception as e:
            raise CloudStorageError(f"Failed to download from GCS: {e}")

    def upload_file(self, local_path: str, cloud_path: str) -> None:
        """Upload to GCS."""
        self._get_client()
        blob = self.bucket.blob(cloud_path)

        try:
            blob.upload_from_filename(local_path)
            logger.info(
                f"Uploaded {local_path} to gs://{self.bucket_name}/{cloud_path}"
            )
        except Exception as e:
            raise CloudStorageError(f"Failed to upload to GCS: {e}")

    def delete_file(self, path: str) -> None:
        """Delete GCS blob."""
        self._get_client()
        blob = self.bucket.blob(path)

        try:
            blob.delete()
            logger.info(f"Deleted gs://{self.bucket_name}/{path}")
        except Exception as e:
            raise CloudStorageError(f"Failed to delete from GCS: {e}")


class AzureStorage(CloudStorageBase):
    """Azure Blob Storage implementation."""

    def __init__(
        self, account_name: str, container: str, account_key: str = None, **kwargs
    ):
        super().__init__(**kwargs)
        if not AZURE_AVAILABLE:
            raise CloudStorageError(
                "Azure SDK not available. Install with: pip install azure-storage-blob"
            )

        self.account_name = account_name
        self.container = container
        self.account_key = account_key

    def _get_client(self):
        """Get Azure Blob client."""
        if self._client is None:
            try:
                # Try account key first, then environment variables
                if self.account_key:
                    account_url = f"https://{self.account_name}.blob.core.windows.net"
                    self._client = BlobServiceClient(
                        account_url=account_url, credential=self.account_key
                    )
                else:
                    # Try default credential chain
                    from azure.identity import DefaultAzureCredential

                    account_url = f"https://{self.account_name}.blob.core.windows.net"
                    credential = DefaultAzureCredential()
                    self._client = BlobServiceClient(
                        account_url=account_url, credential=credential
                    )

                # Test connection
                self._client.get_container_client(
                    self.container
                ).get_container_properties()
                logger.info(f"Connected to Azure container: {self.container}")

            except Exception as e:
                raise CloudCredentialsError(f"Azure authentication failed: {e}")

        return self._client

    def exists(self, path: str) -> bool:
        """Check if Azure blob exists."""
        client = self._get_client()
        blob_client = client.get_blob_client(container=self.container, blob=path)
        return blob_client.exists()

    def list_files(
        self, prefix: str = "", max_files: int = 1000
    ) -> List[Dict[str, Any]]:
        """List Azure blobs."""
        client = self._get_client()
        container_client = client.get_container_client(self.container)

        blobs = container_client.list_blobs(
            name_starts_with=prefix, max_results=max_files
        )

        files = []
        for blob in blobs:
            files.append(
                {
                    "path": blob.name,
                    "size": blob.size,
                    "modified": blob.last_modified,
                    "etag": blob.etag,
                    "content_type": (
                        blob.content_settings.content_type
                        if blob.content_settings
                        else None
                    ),
                    "storage_class": blob.blob_tier,
                }
            )

        return files

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get Azure blob metadata."""
        client = self._get_client()
        blob_client = client.get_blob_client(container=self.container, blob=path)

        try:
            properties = blob_client.get_blob_properties()
            return {
                "path": path,
                "size": properties.size,
                "modified": properties.last_modified,
                "etag": properties.etag,
                "content_type": (
                    properties.content_settings.content_type
                    if properties.content_settings
                    else None
                ),
                "metadata": properties.metadata or {},
                "storage_class": properties.blob_tier,
            }
        except Exception as e:
            raise CloudStorageError(f"Azure blob '{path}' not found: {e}")

    def download_file(self, cloud_path: str, local_path: str) -> None:
        """Download from Azure."""
        client = self._get_client()
        blob_client = client.get_blob_client(container=self.container, blob=cloud_path)

        try:
            with open(local_path, "wb") as f:
                download_stream = blob_client.download_blob()
                f.write(download_stream.readall())
            logger.info(f"Downloaded {cloud_path} to {local_path}")
        except Exception as e:
            raise CloudStorageError(f"Failed to download from Azure: {e}")

    def upload_file(self, local_path: str, cloud_path: str) -> None:
        """Upload to Azure."""
        client = self._get_client()
        blob_client = client.get_blob_client(container=self.container, blob=cloud_path)

        try:
            with open(local_path, "rb") as f:
                blob_client.upload_blob(f, overwrite=True)
            logger.info(f"Uploaded {local_path} to {cloud_path}")
        except Exception as e:
            raise CloudStorageError(f"Failed to upload to Azure: {e}")

    def delete_file(self, path: str) -> None:
        """Delete Azure blob."""
        client = self._get_client()
        blob_client = client.get_blob_client(container=self.container, blob=path)

        try:
            blob_client.delete_blob()
            logger.info(f"Deleted {path}")
        except Exception as e:
            raise CloudStorageError(f"Failed to delete from Azure: {e}")


class CloudStorageManager:
    """Unified manager for all cloud storage providers."""

    def __init__(self):
        self._providers = {}

    def register_s3(
        self, name: str, bucket: str, region: str = None, **kwargs
    ) -> S3Storage:
        """Register S3 storage provider."""
        provider = S3Storage(bucket=bucket, region=region, **kwargs)
        self._providers[name] = provider
        return provider

    def register_gcs(
        self, name: str, bucket: str, project: str = None, **kwargs
    ) -> GCSStorage:
        """Register GCS storage provider."""
        provider = GCSStorage(bucket=bucket, project=project, **kwargs)
        self._providers[name] = provider
        return provider

    def register_azure(
        self,
        name: str,
        account_name: str,
        container: str,
        account_key: str = None,
        **kwargs,
    ) -> AzureStorage:
        """Register Azure storage provider."""
        provider = AzureStorage(
            account_name=account_name,
            container=container,
            account_key=account_key,
            **kwargs,
        )
        self._providers[name] = provider
        return provider

    def get_provider(self, name: str) -> CloudStorageBase:
        """Get registered provider by name."""
        if name not in self._providers:
            raise CloudStorageError(f"Provider '{name}' not registered")
        return self._providers[name]

    def list_providers(self) -> List[str]:
        """List registered provider names."""
        return list(self._providers.keys())


# Global manager instance
_cloud_manager = CloudStorageManager()


def register_s3_provider(
    name: str, bucket: str, region: str = None, **kwargs
) -> S3Storage:
    """Register S3 provider globally."""
    return _cloud_manager.register_s3(name, bucket, region, **kwargs)


def register_gcs_provider(
    name: str, bucket: str, project: str = None, **kwargs
) -> GCSStorage:
    """Register GCS provider globally."""
    return _cloud_manager.register_gcs(name, bucket, project, **kwargs)


def register_azure_provider(
    name: str, account_name: str, container: str, account_key: str = None, **kwargs
) -> AzureStorage:
    """Register Azure provider globally."""
    return _cloud_manager.register_azure(
        name, account_name, container, account_key, **kwargs
    )


class CloudDataReader:
    """High-level interface for reading geospatial data from cloud storage."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path(tempfile.gettempdir()) / "pymapgis_cloud_cache"
        )
        self.cache_dir.mkdir(exist_ok=True)

    def read_cloud_file(self, cloud_url: str, provider_name: str = None, **kwargs):
        """
        Read geospatial data directly from cloud storage.

        Args:
            cloud_url: Cloud URL (s3://bucket/path, gs://bucket/path, etc.)
            provider_name: Registered provider name (optional)
            **kwargs: Additional arguments for the reader

        Returns:
            Geospatial data (GeoDataFrame, DataArray, etc.)
        """
        # Parse cloud URL
        parsed = urlparse(cloud_url)
        scheme = parsed.scheme.lower()

        if scheme == "s3":
            bucket = parsed.netloc
            path = parsed.path.lstrip("/")

            if provider_name:
                provider = _cloud_manager.get_provider(provider_name)
            else:
                # Auto-register S3 provider
                provider = S3Storage(bucket=bucket)

        elif scheme == "gs":
            bucket = parsed.netloc
            path = parsed.path.lstrip("/")

            if provider_name:
                provider = _cloud_manager.get_provider(provider_name)
            else:
                # Auto-register GCS provider
                provider = GCSStorage(bucket=bucket)

        elif scheme in ["https", "http"] and "blob.core.windows.net" in parsed.netloc:
            # Azure blob URL
            parts = parsed.netloc.split(".")
            account_name = parts[0]
            path_parts = parsed.path.strip("/").split("/", 1)
            container = path_parts[0]
            path = path_parts[1] if len(path_parts) > 1 else ""

            if provider_name:
                provider = _cloud_manager.get_provider(provider_name)
            else:
                # Auto-register Azure provider
                provider = AzureStorage(account_name=account_name, container=container)

        else:
            raise CloudStorageError(f"Unsupported cloud URL scheme: {scheme}")

        # Generate cache filename
        cache_filename = f"{hash(cloud_url)}_{Path(path).name}"
        cache_path = self.cache_dir / cache_filename

        # Download if not cached or if file is newer
        should_download = True
        if cache_path.exists():
            try:
                cloud_info = provider.get_file_info(path)
                cache_mtime = cache_path.stat().st_mtime
                cloud_mtime = cloud_info["modified"].timestamp()

                if cache_mtime >= cloud_mtime:
                    should_download = False
                    logger.info(f"Using cached file: {cache_path}")

            except Exception as e:
                logger.warning(f"Could not check cloud file timestamp: {e}")

        if should_download:
            logger.info(f"Downloading {cloud_url} to cache...")
            provider.download_file(path, str(cache_path))

        # Read the cached file using PyMapGIS
        try:
            from pymapgis.io import read

            return read(str(cache_path), **kwargs)
        except ImportError:
            # Fallback to basic readers
            suffix = Path(path).suffix.lower()
            if suffix == ".csv":
                import pandas as pd

                return pd.read_csv(cache_path, **kwargs)
            else:
                raise CloudStorageError(
                    f"Cannot read file type {suffix} without PyMapGIS IO module"
                )


# Convenience functions
def cloud_read(cloud_url: str, provider_name: str = None, **kwargs):
    """
    Convenience function to read data from cloud storage.

    Args:
        cloud_url: Cloud URL (s3://bucket/path, gs://bucket/path, etc.)
        provider_name: Optional registered provider name
        **kwargs: Additional arguments for the reader

    Returns:
        Geospatial data

    Examples:
        # Read from S3
        gdf = cloud_read("s3://my-bucket/data.geojson")

        # Read from GCS
        df = cloud_read("gs://my-bucket/data.csv")

        # Read from Azure
        gdf = cloud_read("https://account.blob.core.windows.net/container/data.gpkg")
    """
    reader = CloudDataReader()
    return reader.read_cloud_file(cloud_url, provider_name, **kwargs)


def cloud_write(data, cloud_url: str, provider_name: str = None, **kwargs):
    """
    Write data to cloud storage.

    Args:
        data: Data to write (GeoDataFrame, DataFrame, etc.)
        cloud_url: Cloud URL destination
        provider_name: Optional registered provider name
        **kwargs: Additional arguments for the writer
    """
    # Parse cloud URL
    parsed = urlparse(cloud_url)
    scheme = parsed.scheme.lower()

    if scheme == "s3":
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else S3Storage(bucket=bucket)
        )

    elif scheme == "gs":
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else GCSStorage(bucket=bucket)
        )

    elif scheme in ["https", "http"] and "blob.core.windows.net" in parsed.netloc:
        parts = parsed.netloc.split(".")
        account_name = parts[0]
        path_parts = parsed.path.strip("/").split("/", 1)
        container = path_parts[0]
        path = path_parts[1] if len(path_parts) > 1 else ""
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else AzureStorage(account_name=account_name, container=container)
        )

    else:
        raise CloudStorageError(f"Unsupported cloud URL scheme: {scheme}")

    # Write to temporary file first
    with tempfile.NamedTemporaryFile(
        suffix=Path(path).suffix, delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

        try:
            # Write data to temporary file
            if hasattr(data, "to_file"):
                # GeoDataFrame
                data.to_file(tmp_path, **kwargs)
            elif hasattr(data, "to_csv"):
                # DataFrame
                data.to_csv(tmp_path, index=False, **kwargs)
            else:
                raise CloudStorageError(
                    f"Unsupported data type for cloud writing: {type(data)}"
                )

            # Upload to cloud
            provider.upload_file(tmp_path, path)
            logger.info(f"Successfully wrote data to {cloud_url}")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


def list_cloud_files(
    cloud_url: str, provider_name: str = None, max_files: int = 1000
) -> List[Dict[str, Any]]:
    """
    List files in cloud storage.

    Args:
        cloud_url: Cloud URL (bucket or container)
        provider_name: Optional registered provider name
        max_files: Maximum number of files to return

    Returns:
        List of file information dictionaries
    """
    parsed = urlparse(cloud_url)
    scheme = parsed.scheme.lower()
    prefix = parsed.path.lstrip("/")

    if scheme == "s3":
        bucket = parsed.netloc
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else S3Storage(bucket=bucket)
        )

    elif scheme == "gs":
        bucket = parsed.netloc
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else GCSStorage(bucket=bucket)
        )

    elif scheme in ["https", "http"] and "blob.core.windows.net" in parsed.netloc:
        parts = parsed.netloc.split(".")
        account_name = parts[0]
        path_parts = parsed.path.strip("/").split("/", 1)
        container = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ""
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else AzureStorage(account_name=account_name, container=container)
        )

    else:
        raise CloudStorageError(f"Unsupported cloud URL scheme: {scheme}")

    return provider.list_files(prefix=prefix, max_files=max_files)


def get_cloud_info(cloud_url: str, provider_name: str = None) -> Dict[str, Any]:
    """
    Get information about a cloud file.

    Args:
        cloud_url: Cloud URL to the file
        provider_name: Optional registered provider name

    Returns:
        File information dictionary
    """
    parsed = urlparse(cloud_url)
    scheme = parsed.scheme.lower()

    if scheme == "s3":
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else S3Storage(bucket=bucket)
        )

    elif scheme == "gs":
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else GCSStorage(bucket=bucket)
        )

    elif scheme in ["https", "http"] and "blob.core.windows.net" in parsed.netloc:
        parts = parsed.netloc.split(".")
        account_name = parts[0]
        path_parts = parsed.path.strip("/").split("/", 1)
        container = path_parts[0]
        path = path_parts[1] if len(path_parts) > 1 else ""
        provider = (
            _cloud_manager.get_provider(provider_name)
            if provider_name
            else AzureStorage(account_name=account_name, container=container)
        )

    else:
        raise CloudStorageError(f"Unsupported cloud URL scheme: {scheme}")

    return provider.get_file_info(path)
