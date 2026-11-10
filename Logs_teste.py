#função Logs

import datetime
dt=datetime.datetime.now()
print(dt)
def logs_erro (idErro,title, message, filepath):
    #data e hora atual 
    dt=datetime.datetime.now()
    
    #Mensagem 
    
    msg = '\n'
    msg += 'ID: ' + str(idErro) + '\n'
    msg += 'Titulo: ' + title + '\n'
    
    #