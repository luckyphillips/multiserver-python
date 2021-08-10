import os
import shutil
import time
import getpass
import sys
import threading


sudo_password=""

class Server:
    def __init__(self,name,ip,port,user,password):
        self.name=name
        self.ip=ip
        self.port=port
        self.user=user
        self.password=password
        
        

class Servers:
    def __init__(self):
        self.hosts = []
        self.servers=[]            
    
    def save_configuration(self):
        c=input("CAUTION! This will print the passwords to the backup file. Do you wish to continue? (Y/n) ")
        if c.upper=="N" or c.upper=="NO": 
            self.menu()
            
        if not os.path.exists(".multiserver"):
            os.makedirs(".multiserver")
        if os.path.isfile(".multiserver/.servers.csv"):
            ts = time.time()
            shutil.copy(".multiserver/.servers.csv",".multiserver/.servers.csv."+str(ts))
            print("A back up of the original \".multiserver/.servers.csv\" has been saved as \".multiserver/.servers.csv."+str(ts))
        f = open(".multiserver/.servers.csv", "w")
        for i in self.servers:
            f.write(i.name.strip()+","+i.ip.strip()+","+i.port.strip()+","+i.user.strip()+","+i.password.strip()+'\r')
        f.close()
        self.menu()
        
    def load_configuration(self):
        if os.path.isfile(".multiserver/.servers.csv"):
            f = open(".multiserver/.servers.csv", "r")
            self.servers=[]
            for x in f:
                s=Server(*x.split(","))
                print(s.name)
                self.servers.append(s)
        self.menu()
                
       
    def show_servers(self):
        with open('/etc/hosts', 'r') as f:
            hostlines = f.readlines()
            hostlines = [line.strip() for line in hostlines if not line.startswith('#') and line.strip() != '']
            host = []
            print()
            print ("{:<3} {:<20} {:<10}".format(' ','[HOSTNAME]','[IP-ADDRESS]'))
            print()
            for line in hostlines:
                if len(' '.join(line.split()).split(" "))==2:
                    hnames=' '.join(line.split()).split(" ")
                    host.append(hnames)
                    print ("{:<3} {:<20} {:<10}".format(len(host), host[len(host)-1][1], host[len(host)-1][0]))
            self.hosts=host


    def menu(self):
        inp=input("Press ENTER to return to menu or 0 to escape: ")
        if inp==0:
            exit
        else:
            self.print_start()
                  
    def show_selected_servers(self):
        c=0
        print ("{:<3} {:<20} {:<15}".format(" ",'[HOSTNAME]','[IP-ADDRESS]'),'[PORT]')
        for i in self.servers:
            print()
            c=c+1
            print("{:<3} {:<20} {:<15} {:<5}".format(str(c),i.name,i.ip,i.port))        
        
    def remove_host(self,host):
        for i in self.servers:
            if i.name == host:
                self.servers.remove(i)
                print("Host "+host+" removed from list")
                
            
    def remove_host_remove(self):
        self.show_selected_servers()
        print("""
    Select the host to remove.
    You can choose the number of the host, or
    You can choose multiple hosts using a , to separate them, or
    You can type the host name you want to remove.
        """)
        option=input("Host/s to remove: ")
        o=[]
        o.extend(self.servers)
        if option.find(",")!=-1:
            for i in option.split(","):
                if i.strip().isdigit():
                    if int(i)<=len(o):
                        self.remove_host(o[(int(i)-1)].name)
                else:
                    self.remove_host(i)
        elif option.strip().isdigit():
            if int(option)<=len(self.servers):
                self.remove_host(o[(int(option)-1)].name)
        else:
            self.remove_host(option)
        self.menu()



            
    def server_details(self,h_name,h_ip):
        port=input("Please Enter SSH Port for "+h_name+" (Default 22): ") or "22"
        self.port=port
        user=input("Please Enter user for "+h_name+" (Default "+os.getlogin()+"): ") or os.getlogin()
        self.user=user
        print("Please Enter password for "+h_name+": ")
        password=getpass.getpass()
        self.password=password
        s=Server(h_name.strip(),h_ip.strip(),port.strip(),user.strip(),password.strip())
        self.servers.append(s)
        print()
    
    def add_server_from_hosts(self, option):
        option=int(option)
        
        name=self.hosts[option-1][1]
        if self.Server_exists(name)==False:
            ip=self.hosts[option-1][0]
            self.server_details(name,ip)
        else:
            print("Host "+name+" already listed")
        
    def Server_exists(self,h_name):
        for i in self.servers:
            if i.name==h_name:
                return True
        return False

    def add_server(self):
        self.show_servers()
        print("""
    Select a Server number from the hosts provided,
    choose multiple servers from the list provided above using a ',' to serarate them
    or just enter a server name you wish to add.
            """)
        option=input("Enter: ")
        if option.find(",")!=-1:
            for i in option.split(","):
                if int(i)<=len(self.hosts):
                    self.add_server_from_hosts(i)
        else:
            if option.strip().isdigit():
                if int(option)<len(self.hosts):                    
                    self.add_server_from_hosts(option)
            else:
                if self.Server_exists(option)==False:
                    ip=input("Enter IP for host "+option+": ")
                    self.server_details(option,ip)
                else:
                    print("Host "+option+" already listed")
                
        self.print_start()
        
    def get_server(self,name):
        for i in self.servers:
            if i.name==name:
                return i
                            
    def send_command_send(self,hosts,cmd):        
        try:
            runit="echo "+sudo_password+"|sudo -S su "+getpass.getuser()+" -c \"sshpass -p "+str(hosts.password.strip())+" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 "+hosts.user+"@"+hosts.name+" 'echo \""+hosts.password.strip()+"\" | sudo -Sv && "+cmd+"'\" > /dev/null"
            os.system(runit)            
        except:
            print("Could not connect")
    
    def send_command(self):
        t=[]
        self.show_selected_servers()
        option=input("Choose servers to send command to. 0 for ALL: ")
        if option.find(",")!=-1:
            cmd=input("Command to send: ")
            for i in option.split(","):                
                if i.strip().isdigit() and int(i)<=len(self.servers):
                    thread=threading.Thread(target=self.send_command_send, args=(self.servers[int(i)-1], cmd,)).start()
                else:
                    thread=threading.Thread(target=self.send_command_send, args=(self.get_server(i), cmd,)).start()
            for j in t:
                j.join()
        else:
            if option.strip().isdigit() and int(option)!=0:
                if int(option)<=len(self.servers):                    
                    cmd=input("Command to send: ")
                    self.send_command_send(self.servers[int(option)-1],cmd)
            elif option.strip().isdigit() and int(option)==0:
                cmd=input("Command to send: ")
                for i in self.servers:
                    thread=threading.Thread(target=self.send_command_send, args=(i, cmd,)).start()
                for j in t:
                    j.join()
            else:
                cmd=input("Command to send: ")
                self.send_command_send(self.get_server(option),cmd).start
        self.menu()                


        
    def print_start(self):            
        print()
        print("""
        Choose from the menu which you want to deploy

        1 - Add servers
        2 - Remove server
        3 - Show servers
        4 - Send commands
        5 - Load configuration
        6 - Save configuration
        0 - Quit
        """)
        option = input("Choose Option : ")    
        if option=="1":
            self.add_server()
        elif option=="2":
            self.remove_host_remove()
        elif option=="3":
            self.show_selected_servers()
            self.menu()
        elif option=="4":
            self.send_command()            
        elif option=="5":
            self.load_configuration()
        elif option=="6":
            self.save_configuration()
        elif option=="0":            
            exit
        else:
            self.print_start()

print("You must enter your SUDO password to continue this script")
print("Password for Sudo: ")
sudo_password=getpass.getpass()


s=Servers()
s.print_start()



    
