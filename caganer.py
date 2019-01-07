#!/usr/bin/python
# -*- coding: utf-8 -*-

# CAGANER DEL PI
# Pessebre vivent Bonmatí - Desembre de 2018
# Desenvolupar per Xavier Sarsanedas Trias

# Importació de llibreries per poder executar el programa
import RPi.GPIO as GPIO
import time
import pygame
import random
import sys

# Inicialitzem la llibreria pygame que s'encarregarà de reproduïr els sons
pygame.init()
pygame.mixer.init()

# Indiquem en quin mode volem indicar els pins GPIO (BOARD: per número de pin físic / BCM: per nomenclatura segons model de placa raspberry)
GPIO.setmode(GPIO.BCM)

# Constants
NUM_MESURES_MITJANA = 10 # número de mesures de distàncies que es prendran a l'inici d'execució de programa per determinar la distància màxima
ESPERA_ENTRE_MESURES = 1 # temps (en segons) d'espera abans de realitzar una nova mesura de distàncies
PERCENTATGE_DISTANCIA_ERROR = 40 # percentatge que s'utilitzarà per calcular el marge d'error
TEMPS_MOSTRANT_CAGANER = 5 # segons en què estarà el llum encès després de sentir-se el so del pet

# Constants on indiquem quins pins GPIO utilitzarem per connectar el sensor d'ultrasons i el relé: pel trigger (emissor), l'echo (receptor) del senyal i relé
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_RELAY = 25
 
# Indiquem en aquests tres pins quin serà senyal de sortida i quin serà d'entraad (GPIO: IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_RELAY, GPIO.OUT)
 
# Funció que ens retornarà la distància que hi ha entre el sensor d'ultrasons i l'objecte que tingui al davant
def getDistancia():

    # Iniciem l'enviament de senyal pel pin on tenim conectat el trigger (set Trigger to HIGH)
    GPIO.output(GPIO_TRIGGER, True)
 
    # Esperem un instant de temps que mantindrem enviant senyal pel pin del trigger 
    time.sleep(0.00001)

    # Després de 0.01 milisegons, deixem d'enviar senyal (set Trigger to LOW)
    GPIO.output(GPIO_TRIGGER, False)
 
    # Inicialitzem dos variables:
    # TempsInici: per recollir el temps quan s'ha començat a rebre pel pin d'echo el senyal que havíem enviat per trigger (comencem a rebre el rebot del so)
    # TempsFinal: per recollir el temps quan s'ha acabat de rebre pel pin d'echo el senyal que havíem enviat per trigger (acabem de rebre el rebot del so)
    temps_inici = time.time()
    temps_final = time.time()
 
    # Iteració infinita que s'anirà realitzant fins que comencem a rebre el senyal pel pin d'echo 
    # Quan es surti de la iteració, el valor guardat a TempsInici serà considerat el moment d'inici de recepció de senyal)
    while GPIO.input(GPIO_ECHO) == 0:
        temps_inici = time.time()
 
    # Iteració infinita que s'anirà realitzant fins que  detectem que pel pin d'echo ja no arriba senyal
    # Quan es surti de la iteració, el valor guardat a TempsFinal serà considerat el moment que ja hem deixat de rebre senyal)
    while GPIO.input(GPIO_ECHO) == 1:
        temps_final = time.time()
 
    # La diferència entre aquests dos temps, ens indica el temps que ha trigat a viatjar el senyal per l'aire (enviar-lo, rebotar i rebre'l)
    temps_transcorregut = temps_final - temps_inici

    # Multiplicarem el valor del TempsTranscorregut per la velocitat del so (34300 cm/s) per obtenir la distància que recorregut el so emès
    # I finalment dividirem el valor per 2, ja que no ens interessa la dinstància d'anada + tornada (només en interessa saber la distància en un sentit)
    distancia = (temps_transcorregut * 34300) / 2

    return distancia

# Funció que realitzarà un nombre de mesures consecutives i ens calcularà la distància mitjana entre totes elles
def getDistanciaMitjana(num_mesures):

    dist = 0

    for x in range (0, num_mesures):
        dist = dist + getDistancia()
        time.sleep(ESPERA_ENTRE_MESURES)

    return dist / num_mesures

 
# Mètode principal del programa
if __name__ == '__main__':
    try:

        print ("INICIALITZANT...")

        # Carraguem en una llista els fitxers d'àudio (pets) que es prodran reproduïr
        llista_sons = [pygame.mixer.Sound("pet1.ogg"), 
                       pygame.mixer.Sound("pet2.ogg"), 
                       pygame.mixer.Sound("pet3.ogg"),
                       pygame.mixer.Sound("pet4.ogg"),
                       pygame.mixer.Sound("pet5.ogg"),
                       pygame.mixer.Sound("pet6.ogg"),
                       pygame.mixer.Sound("pet7.ogg"),
                       pygame.mixer.Sound("pet8.ogg"),
                       pygame.mixer.Sound("pet9.ogg"),
                       pygame.mixer.Sound("pet10.ogg")]
        num_llista_sons = len(llista_sons)

        # En arrencar el programa, farem algunes mesures sense obstacles davant del sensor per determinar quina és la distància mitjana sense obstacles
        dist_mitjana = getDistanciaMitjana(NUM_MESURES_MITJANA)

        # Mostrem per pantalla el valor obtingut en centímetres amb un decimal
        print ("Distancia mitjana = %.1f cm" % dist_mitjana)

        # Pot haver un marge de la distància màxima que pot fluctuar, reduïm la distància màxima trobada un percentatge concret
        marge_error = dist_mitjana * PERCENTATGE_DISTANCIA_ERROR / 100
        dist_mitjana = dist_mitjana - marge_error
 
        # Mostrem per pantalla el valor obtingut en centímetres amb un decimal (amb el marge d'error aplicat)
        print ("Distancia mitjana = %.1f cm (amb marge d'error aplicat del %d percent)" % (dist_mitjana, PERCENTATGE_DISTANCIA_ERROR))

        # Donarem senyal al relé durant 2 segons per encendre la llum com a senyal per indicar que ja està llest per funcionar
        GPIO.output(GPIO_RELAY, True)
        time.sleep(2)
        GPIO.output(GPIO_RELAY, False)

        # Inicialitzem variables de distància al valor màxim possible que pot guardar-hi el sistema
        dist = sys.maxsize;
        dist_anterior = sys.maxsize;

        # Comencem la detecció de visitants que passen per davant del sensor
        while True:

            # Guardem la distància actual com la distància de l'anterior mesura
            dist_anterior = dist;

            # Obtenim una nova distància
            dist = getDistancia()

            # Mostrem per pantalla el valor obtingut en centímetres amb un decimal
            print ("Distancia: %.1f - %.1f = %.1f" % (dist, dist_mitjana, dist - dist_mitjana))

            if dist < dist_mitjana and dist_anterior < dist_mitjana:
                print ("HA PASSAT ALGÚ!")

                # 0 - Obtenim de forma random un dels possibles sons a reproduïr
                index_llista_sons = random.randint(0, num_llista_sons-1)
                so_pet = llista_sons[index_llista_sons]
                # 1 - Obtenim la durada del so que reproduïrem
                durada_so = so_pet.get_length()
                # 2 - Reproduïr so
                so_pet.play()
                # 3 - Esperar uns segons (fins que acabi la reproducció del so)
                time.sleep(durada_so)
                # 4 - Obrir llum (donar senyal al relé)
                GPIO.output(GPIO_RELAY, True)  
                # 5 - Esperar uns segons
                time.sleep(TEMPS_MOSTRANT_CAGANER)
                # 6 - Tancar llum (tornar a l'estat anterior el relé)
                GPIO.output(GPIO_RELAY, False)
                # 7 - Tornar a detectar si passa algú per davant del sensor d'ultrasons
                dist = sys.maxsize;
                time.sleep(3);

            time.sleep(ESPERA_ENTRE_MESURES)

    except KeyboardInterrupt:
        # Quan es rebi un CTRL + C es llançarà aquesta excepció, fet que provocarà l'aturada del programa
        print("S'ha rebut senyal d'aturada")
    finally:
        # Independentment de com acabi l'execució del programa, sempre acabarà executant aquest codi
        GPIO.cleanup() # resetegem els pins GPIO
        pygame.quit() # alliberem recursos de la llibreria de reproducció de sons
        print ("S'han resetejat els estats dels pins GPIO")
        print ("Programa aturat")

