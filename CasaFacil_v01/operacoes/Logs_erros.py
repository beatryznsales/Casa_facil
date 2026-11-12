#função Logs

import datetime

def logs_erro (idErro,title, message, filepath):
    #data e hora atual 
    dt=datetime.datetime.now()
    
    #Mensagem 
    
    msg = '\n'
    msg += 'ID: ' + str(idErro) + '\n'
    msg += 'Titulo: ' + title + '\n'
    msg += 'Timestamp_1: ' + str(dt) + '\n'
    msg += '\n' 
    msg += 'Mensagem: ' + message + '\n'
    msg += '\n'
    
    
    #Registo
    fileLogs = open(filepath, 'a')
    fileLogs.write(msg)
    fileLogs.close()