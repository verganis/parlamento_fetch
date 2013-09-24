import difflib
from email.mime.text import MIMEText
import json
import smtplib


def send_error_mail(script_name, smtp_server, notification_system, address_list, error_mail_body):

    # se c'e' stato qualche errore manda la mail agli amministratori di sistema

    error_keys = error_mail_body.keys()
    content_str =""
    error_c = 0
    for error_key in error_keys:
        # serializza i msg di errori
        if len(error_mail_body[error_key])>0:
            for msg in error_mail_body[error_key]:
                content_str+=error_key+" : "+msg+"\n"
                error_c+=1


    if error_c>0:
        print "errors"
        send_email(smtp_server,
                   notification_system,
                   address_list,
                   subject= script_name + " - " + str(error_c) +" errori",
                   content= content_str
        )
    else:
        print "no errors"



def send_email(smtp_server, notification_system, address_list, subject, content):

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = notification_system['name']
    msg['To'] = "Admin"

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(smtp_server)
    err = s.sendmail(notification_system['name'], address_list, msg.as_string())
    s.quit()
    return err




def write_file(filename, results,fields=None,print_metadata=True,Json=False):

    # output su file
    outputfile = open(filename,'w')

    if Json is True:
        outputfile.write("%s" % json.dumps(results, indent=0, sort_keys=True))
    else:
        if results:
            if not fields:
                fields= results[0].keys()

            #stampa i metadati
            if print_metadata:
                for index, variable in enumerate(fields):
                    outputfile.write('"%s"' % variable)
                    if index < len(fields):
                        outputfile.write(",")

                outputfile.write("\n")

            #stampa i valori
            for r in results:
                for field in fields:
                    if field in r.keys():
                        outputfile.write('"%s"' % unicode(r[field]).encode("utf-8"))
                    outputfile.write(',')
                outputfile.write("\n")

    outputfile.close()


def create_diff(filename1, filename2):

    with open(filename1, 'r') as file1:
        content1 = file1.read().splitlines()
    with open(filename2, 'r') as file2:
        content2 = file2.read().splitlines()

    # trova le differenze fra i due file

    diff = difflib.unified_diff(
        content1,
        content2,
        n=0,
        fromfile=filename1,
        tofile=filename2,
        lineterm='')

    return '\n'.join(list(diff))

