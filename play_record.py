import subprocess, shlex
import RPi.GPIO as GPIO

def configure_gpio():
	#Configuración de los GPIO de la Raspberry
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(3, GPIO.IN)
	GPIO.output(18, False)

#Función para verificar si hay archivos que no se han subido a Google Drive
def verify_nonupload_archives(route2):
	print("-------------VERIFICANDO-------------")
	#Se abre el archivo de texto
	file2 = open(route2, "r")
	#Se lee el contenido y se guarda en una lista
	name_archives = file2.readlines()
	if len(name_archives) == 0:
		print("No hay archivos para subir")
	else:
		print("Hay archivos para subir")
	#Se extrae el número de archivo y se pasa a la función upload_sound
	for index in name_archives:
		if len(index) == 12:
			archive_number4 = int(name_archives[name_archives.index(index)][6])
		elif len(index) == 13:
			archive_number4 = int(name_archives[name_archives.index(index)][6:8])
		elif len(index) == 14:
			archive_number4 = int(name_archives[name_archives.index(index)][6:9])
		elif len(index) == 15:
			archive_number4 = int(name_archives[name_archives.index(index)][6:10])
		upload_sound(archive_number4)
	#Se cierra el archivo
	file2.close()
	#Se abre nuevamente el archivo, pero vacio
	file2 = open(route2, "w")
	#Se extrae nuevamente el número de archivo
	for line in name_archives:
		if len(line) == 12:
			number = name_archives[name_archives.index(line)][6]
		elif len(line) == 13:
			number = name_archives[name_archives.index(line)][6:8]
		elif len(line) == 14:
			number = name_archives[name_archives.index(line)][6:9]
		elif len(line) == 15:
			number = name_archives[name_archives.index(line)][6:10]
		#Se verifica si el nombre de archivo coincide con la linea que se quiere eliminar
		if not line == 'prueba' + number + '.wav' + '\n':
			#Si no es la linea que se quiere eliminar, se guarda la linea en el archivo
			file2.write(line)
	#Se cierra el archivo
	file2.close()

#Si no hay conexión a Internet, se guarda el nombre de los archivos en un archivo de texto para luego subirlos a Google Drive
def if_notconnected(file, archive_number4):
	content = 'prueba' + str(archive_number4) + '.wav' + '\n'
	file.writelines(content)

def count_archives(archive_number1):
	#Ciclo while para cambiar o no el valor de contador de archivos de audio
	while True:
		#Comando de terminal para verificar la existencia de un archivo de audio o no
		command_line3 = '[ -f /home/pi/scripts/prueba' + str(archive_number1) + '.wav ]'
		args1 = shlex.split(command_line3)
		existance = subprocess.call(args1)
		if existance == 0:
			archive_number1 += 1
		elif existance == 1:
			break
	return archive_number1

#Función para la verificación de la conexión a internet
def verify_conection(host):
	command = 'ping -c 3 -W 5 {}'.format(host)
	args32 = shlex.split(command)
	# connected = 0 si hay conexión. connected = 2 si no hay conexión
	connected = subprocess.call(args32, stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
	return connected == 0

#Función para la grabación de audio
def record_function(time_duration, archive_number2):
	#Se apaga el LED, indicando el inicio de la grabación
	GPIO.output(18, False)
	#Comando de terminal para la grabación
	command_line1 = 'sudo arecord -D plughw:1 -d ' + str(time_duration) + ' -c1 -r 24000 -f S32_LE -t wav -V mono -v prueba' + str(archive_number2) + '.wav'
	args2 = shlex.split(command_line1)
	#Inicio de la grabación durante time_duration segundos"
	subprocess.call(args2)

#Función para subir el archivo a Drive u otros
def upload_sound(archive_number3):
	print("Conectado a Internet")
	#Comando de terminal para subir el archivo de audio a Google Drive
	command_line2 = 'sudo rclone copy /home/pi/scripts/prueba' + str(archive_number3) + '.wav gdriveuni:PruebaRaspberry'
	args3 = shlex.split(command_line2)
	print("Subiendo.............")
	#Subiendo el archivo a Google Drive
	subprocess.call(args3)
	print("Subido...")

#Función principal del script
def record_now():
	configure_gpio()

	#Tiempo de grabación
	time_duration = 10

	#Inicio del contador de archivos de audio
	archive_number = 1

	archive_number = count_archives(archive_number)

	#Servidor(Google) para la verificación de la conexión a internet
	host = '8.8.8.8'

	route = '/home/pi/scripts/noupload_archives.txt'

	if verify_conection(host):
		print("Empieza la subida")
		verify_nonupload_archives(route)
		print("Termina la subida")
	else:
		pass

	file = open(route, "a")

	try:
		while True:
			print("Se enciende el LED")
			#Encendido del LED para verificar la disponibilidad del micrófono
			GPIO.output(18, True)

			while True:
				if not GPIO.input(3):
					record_function(time_duration, archive_number) #Grabación de audio
					#Se verifica la conexión a internet
					if verify_conection(host):
						upload_sound(archive_number) #Subida del archivo a Drive
					else:
						print("No hay conexión a Internet")
						if_notconnected(file, archive_number)
					archive_number += 1
					break
				else:
					pass
			print("-------------------Record Ended. NEXT---------------------")
			#Se vuelve a encender el LED para indicar la disponibilidad para una nueva grabación
			GPIO.output(18, True)
		file.close()
	except KeyboardInterrupt:
		print("----------------Record Aborted------------------")
	finally:
		print("----------------Record ended defenitivily------------------")
		GPIO.cleanup()

#Inicio del programa
if __name__ == "__main__":
	record_now()

