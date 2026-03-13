from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from database import (
    create_box,
    add_item,
    get_boxes,
    get_boxes_with_counts,
    get_box,
    get_items_in_box,
    get_item,
    get_box_of_item,
    increase_quantity,
    decrease_quantity,
    update_item_quantity,
    update_box_data,
    update_item_data,
    delete_item_by_id,
    delete_box_by_id,
    get_statistics,
    search_all,
    move_item_to_box,
)
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def normalize_text(value: str) -> str:
    return (value or "").strip()


def parse_positive_int(value, default=1):
    try:
        number = int(value)
        return number if number > 0 else default
    except (TypeError, ValueError):
        return default


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(photo):
    if not photo or photo.filename == "":
        return None
    if not allowed_file(photo.filename):
        return None
    safe_name = secure_filename(photo.filename)
    filename = f"{uuid.uuid4()}_{safe_name}"
    photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename


def delete_image_if_needed(filename):
    if not filename or filename == "none":
        return
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)


@app.context_processor
def inject_globals():
    return {"all_boxes_for_nav": get_boxes()}


@app.route("/")
def index():
    boxes_data = get_boxes_with_counts()
    stats = get_statistics()
    return render_template("index.html", boxes_data=boxes_data, stats=stats)


@app.route("/box/<int:box_id>")
def box(box_id):
    selected_box = get_box(box_id)
    if not selected_box:
        return redirect(url_for("index"))
    items = get_items_in_box(box_id)
    boxes = [b for b in get_boxes() if b.id != box_id]
    return render_template("box.html", box=selected_box, items=items, boxes=boxes)


@app.route("/add_box", methods=["GET", "POST"])
def add_box_route():
    if request.method == "POST":
        name = normalize_text(request.form.get("name")) or "קופסא חדשה"
        filename = save_uploaded_image(request.files.get("photo"))
        create_box(name, filename)
        return redirect(url_for("index"))
    return render_template("add_box.html")


@app.route("/add_item/<int:box_id>", methods=["POST"])
def add_item_route(box_id):
    box_obj = get_box(box_id)
    if not box_obj:
        return redirect(url_for("index"))

    name = normalize_text(request.form.get("name"))
    if not name:
        return redirect(url_for("box", box_id=box_id))

    quantity = parse_positive_int(request.form.get("quantity"), default=1)
    filename = save_uploaded_image(request.files.get("photo"))
    add_item(name, box_id, filename, quantity)
    return redirect(url_for("box", box_id=box_id))


@app.route("/increase/<int:item_id>")
def increase(item_id):
    box_obj = get_box_of_item(item_id)
    if not box_obj:
        return redirect(url_for("index"))
    increase_quantity(item_id)
    return redirect(url_for("box", box_id=box_obj.id))


@app.route("/decrease/<int:item_id>")
def decrease(item_id):
    box_obj = get_box_of_item(item_id)
    if not box_obj:
        return redirect(url_for("index"))
    decrease_quantity(item_id)
    return redirect(url_for("box", box_id=box_obj.id))


@app.route("/update_quantity/<int:item_id>", methods=["POST"])
def update_quantity(item_id):
    item = get_item(item_id)
    if not item:
        return redirect(url_for("index"))
    quantity = parse_positive_int(request.form.get("quantity"), default=item.quantity)
    update_item_quantity(item_id, quantity)
    return redirect(url_for("box", box_id=item.box.id))


@app.route("/move_item/<int:item_id>", methods=["POST"])
def move_item(item_id):
    item = get_item(item_id)
    if not item:
        return redirect(url_for("index"))
    new_box_id = parse_positive_int(request.form.get("box_id"), default=item.box_id)
    move_item_to_box(item_id, new_box_id)
    return redirect(url_for("box", box_id=new_box_id))


@app.route("/delete_item/<int:item_id>")
def delete_item(item_id):
    result = delete_item_by_id(item_id)
    if not result:
        return redirect(url_for("index"))
    delete_image_if_needed(result["photo"])
    return redirect(url_for("box", box_id=result["box_id"]))


@app.route("/delete_box/<int:box_id>")
def delete_box(box_id):
    result = delete_box_by_id(box_id)
    if result:
        for photo in result["photos"]:
            delete_image_if_needed(photo)
    return redirect(url_for("index"))


@app.route("/edit_box/<int:box_id>", methods=["GET", "POST"])
def edit_box(box_id):
    box_obj = get_box(box_id)
    if not box_obj:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = normalize_text(request.form.get("name")) or box_obj.name
        new_filename = save_uploaded_image(request.files.get("photo"))
        old_photo = box_obj.photo
        update_box_data(box_id, name, photo=new_filename if new_filename else old_photo)
        if new_filename and old_photo != new_filename:
            delete_image_if_needed(old_photo)
        return redirect(url_for("box", box_id=box_id))

    return render_template("edit_box.html", box=box_obj)


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = get_item(item_id)
    if not item:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = normalize_text(request.form.get("name")) or item.name
        quantity = parse_positive_int(request.form.get("quantity"), default=item.quantity)
        new_filename = save_uploaded_image(request.files.get("photo"))
        old_photo = item.photo
        update_item_data(item_id, name, quantity=quantity, photo=new_filename if new_filename else old_photo)
        if new_filename and old_photo != new_filename:
            delete_image_if_needed(old_photo)
        return redirect(url_for("box", box_id=item.box_id))

    return render_template("edit_item.html", item=item)


@app.route("/search")
def search():
    query = normalize_text(request.args.get("q"))
    results = search_all(query, limit=100)
    return render_template("search.html", items=results["items"], boxes=results["boxes"], query=query)


@app.route("/api/search")
def api_search():
    query = normalize_text(request.args.get("q"))
    results = search_all(query, limit=8)
    return jsonify({
        "boxes": [
            {
                "id": box.id,
                "name": box.name,
                "photo": box.photo,
                "url": url_for("box", box_id=box.id),
                "type": "box",
            }
            for box in results["boxes"]
        ],
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "box_id": item.box.id,
                "box_name": item.box.name,
                "url": url_for("box", box_id=item.box.id),
                "type": "item",
            }
            for item in results["items"]
        ],
    })


@app.route("/sw.js")
def service_worker():
    return app.send_static_file("pwa/sw.js")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5070, debug=True)
