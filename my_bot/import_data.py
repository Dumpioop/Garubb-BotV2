from database import Database

db = Database("bot.db")
db.import_excel("participants.xlsx")

print("Excel data imported successfully!")