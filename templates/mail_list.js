{"Mails":[{% for m in mails %}{"Id":{{m.id}},"Txt":"{{m.txt}}"},{% endfor %}]}