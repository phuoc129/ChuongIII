import os           
import shutil       
import datetime     
import schedule     
import time         
from dotenv import load_dotenv  
import smtplib      
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  

load_dotenv()

# Lay thong tin tu bien moi truong de su dung trong email
SENDER_EMAIL = os.getenv('SENDER_EMAIL')    
APP_PASSWORD = os.getenv('APP_PASSWORD')    
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SMTP_SERVER = "smtp.gmail.com"              
SMTP_PORT = 587                             

# Dinh nghia cac thu muc cho csdl va sao luu
DATABASE_DIR = "./databases" 
BACKUP_DIR = "./backup"      

# Hàm gửi email
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        #ket noi toi server SMTP, su dung TLS de bảo mật ket noi
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Gui email thanh cong!")
        return True
    except Exception as e:
        print(f"Loi khi gui email: {e}")
        return False

#Ham sao luu csdl
def backup_databases():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")  

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    files = os.listdir(DATABASE_DIR)
    db_files = [f for f in files if f.endswith('.sql') or f.endswith('.sqlite3')]

    success = True
    report = []

    if not db_files:
        report.append("Khong tim thay database!")
        success = False

    for db_file in db_files:
        try:
            src = os.path.join(DATABASE_DIR, db_file)
            dest_name = f"{db_file.split('.')[0]}_{timestamp}.{db_file.split('.')[-1]}"
            dest = os.path.join(BACKUP_DIR, dest_name)
            shutil.copy2(src, dest)
            report.append(f"Da sao luu {db_file} vao {dest_name}")
        except Exception as e:
            report.append(f"Khong the sao luu {db_file}: {e}")
            success = False

    subject = "Bao cao sao luu - " + ("Thanh cong" if success else "That bai")
    body = "\n".join(report)
    send_email(subject, body)

#Ham thuc thi lich trinh sao luu
def job():
    print("Bat dau luu vao luc", datetime.datetime.now())
    backup_databases()

schedule.every().day.at("00:00").do(job)

print("Khoi dong lich trinh sao luu...")
while True:
    schedule.run_pending()
    time.sleep(60)
