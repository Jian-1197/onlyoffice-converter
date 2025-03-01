import os
import uuid
import requests
from flask import Flask, request, send_file, jsonify, send_from_directory

app = Flask(__name__)
temp_dir = "/app/tmp"
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # 生成唯一ID
    temp_id = str(uuid.uuid4())
    input_filename = f"{temp_id}.docx"
    input_path = os.path.join(temp_dir, input_filename)
    output_filename = f"{temp_id}.pdf"
    output_path = os.path.join(temp_dir, output_filename)
    
    try:
        # 保存上传文件
        file.save(input_path)
        
        # 构造转换请求
        convert_url = "http://localhost/ConvertService.ashx"
        payload = {
            "async": False,
            "filetype": "docx",
            "key": temp_id,
            "outputtype": "pdf",
            "title": input_filename,
            "url": f"http://localhost:5000/temp/{input_filename}"
        }
        
        # 发送转换请求
        response = requests.post(convert_url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get('error'):
            return jsonify({"error": result['error']}), 500
        
        # 下载转换结果
        pdf_response = requests.get(result['fileUrl'])
        pdf_response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(pdf_response.content)
            
        return send_file(output_path, mimetype='application/pdf', as_attachment=True, download_name='converted.pdf')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # 清理临时文件
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

@app.route('/temp/<filename>')
def serve_temp(filename):
    return send_from_directory(temp_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
