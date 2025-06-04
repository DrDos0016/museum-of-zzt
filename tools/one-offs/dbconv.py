import MySQLdb
# This script was used to update database tables to utf8mb4. Credentials have been removed before adding to repo.

# DEV
host = "localhost"
passwd = ""
user = ""
dbname = ""

db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)
cursor = db.cursor()

cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci'" % dbname)

sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
print(sql)
cursor.execute(sql)

results = cursor.fetchall()
for row in results:
  sql = "ALTER TABLE `%s` convert to character set utf8mb4 COLLATE utf8mb4_general_ci" % (row[0])
  print(sql)
  cursor.execute(sql)
db.close()
