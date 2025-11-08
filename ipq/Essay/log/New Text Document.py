import csv

# Read content from 'log.txt'
with open(r'D:\User\Desktop\JTST\ipq\Essay\log\log.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Split content into date-comment pairs
entries = [entry.strip() for entry in content.split('\n\n') if entry.strip()]

# Write data to CSV
csv_file_path = r'D:\User\Desktop\JTST\ipq\Essay\log\log.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Date', 'Comment'])  # Write header
    for entry in entries:
        date, *comment_lines = entry.split('\n')
        comment = ' '.join(comment_lines)
        csv_writer.writerow([date, comment])
