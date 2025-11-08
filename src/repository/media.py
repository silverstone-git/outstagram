
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from ...lib.s3_client import S3ClientManager
from uuid import uuid4
import time
from typing import List

s3_manager = S3ClientManager()
s3_client = s3_manager.get_client()
s3_bucket = s3_manager.get_bucket()

def upload_media_to_s3(file: UploadFile, db: Session):
    
    file_extension = file.filename.split('.')[-1]
    object_key = f"{int(time.time())}-{uuid4()}.{file_extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            s3_bucket,
            object_key,
            ExtraArgs={'ContentType': file.content_type, 'ACL': 'public-read'}
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket, 'Key': object_key},
            ExpiresIn=604800  # 7 days
        )

        return {"object_key": object_key, "presigned_url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

def upload_media_bulk_to_s3(files: List[UploadFile], db: Session):
    
    results = []
    for file in files:
        results.append(upload_media_to_s3(file, db))
    
    return results
