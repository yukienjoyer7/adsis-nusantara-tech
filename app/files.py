from flask import Blueprint, request, jsonify, redirect
from flask_login import login_required, current_user
from db import db
from models import File
from storage import get_minio, get_minio_public, BUCKET

files_bp = Blueprint("files", __name__)


@files_bp.post("/files")
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_key = f"{current_user.id}/{f.filename}"
    get_minio().upload_fileobj(f, BUCKET, file_key)

    record = File(student_id=current_user.id, file_key=file_key, original_name=f.filename)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "id": record.id,
        "file_key": record.file_key,
        "original_name": record.original_name,
        "uploaded_at": record.uploaded_at.isoformat(),
    }), 201


@files_bp.get("/files")
@login_required
def list_files():
    records = (
        File.query
        .filter_by(student_id=current_user.id)
        .order_by(File.uploaded_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": r.id,
            "file_key": r.file_key,
            "original_name": r.original_name,
            "uploaded_at": r.uploaded_at.isoformat(),
        }
        for r in records
    ])


@files_bp.get("/files/<path:file_key>")
@login_required
def download_file(file_key):
    full_key = f"{current_user.id}/{file_key}"
    record = File.query.filter_by(student_id=current_user.id, file_key=full_key).first()
    if record is None:
        return jsonify({"error": "File not found"}), 404

    url = get_minio_public().generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": full_key},
        ExpiresIn=3600,
    )
    return redirect(url)


@files_bp.delete("/files/<path:file_key>")
@login_required
def delete_file(file_key):
    full_key = f"{current_user.id}/{file_key}"
    record = File.query.filter_by(student_id=current_user.id, file_key=full_key).first()
    if record is None:
        return jsonify({"error": "File not found"}), 404

    db.session.delete(record)
    db.session.commit()
    get_minio().delete_object(Bucket=BUCKET, Key=full_key)
    return jsonify({"message": "Deleted"})
