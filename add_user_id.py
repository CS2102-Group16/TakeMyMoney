"""
Helper module by Teddy. You can safely ignore this or approach me if you don't understand
and wish to know more
"""
import random

with open('projects.sql', 'r') as f:
    count = 1
    sqls = []
    for line in f:
        idx = line.index('title')
        line = line[:idx] + 'id, ' + line[idx:]
        idx = line.index('VALUES (') + len('VALUES (')
        line = line[:idx] + str(count) + ', ' + line[idx:]
        idx = line.index('photo_url)') + len('photo_url')
        line = line[:idx] + ', user_id' + line[idx:]
        idx = line.index(');')
        line = line[:idx] + ', ' + str(random.randint(1, 20)) + line[idx:]
        sqls.append(line)
        count += 1

with open('projects.new.sql', 'w') as f:
    f.writelines(sqls)