#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import time

logger = logging.getLogger('')

IDENTICICATION = 'Roto'
IMPULS = 1
UP = 0
DOWN = 1
OFF = 2




class Roto():

    def __init__(self, smarthome):
        self._sh = smarthome
        self.__roto_items = {}

    def run(self):
        self.alive = True
        count_items = 0
        for item in self._sh.find_items("roto_plugin"):
            if item.conf["roto_plugin"] == "active":
                try:
                    roto_item = RotoItem(self._sh, item)
                    self.__roto_items[roto_item.id] = roto_item
                    count_items += 1
                except ValueError as ex:
                    logger.error("Item: {0}: {1}".format(item.id(), str(ex)))
                    
        logger.info("Using Roto for {0} Items".format(count_items))    

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'roto_plugin' in item.conf and item.conf["roto_plugin"] == "active":
            return self.update_item 
            #logger.debug("parse item: {0}".format(item))
        else:
            return None

    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass
        
    def update_item(self, item, caller=None, source=None, dest=None):
        orig_caller, orig_source, orig_item = self.get_original_caller(self._sh, caller, source, item)
        
        if orig_caller == IDENTICICATION or caller == IDENTICICATION:
            logger.debug("Ignoring changes from " + IDENTICICATION)
            return
       
        #logger.info("update item: {0}".format(item.id()))
        item_source = self._sh.return_item(source)
        if item.id() in self.__roto_items:
            roto_item = self.__roto_items[item.id()]
        else:
            return
        
        if (source == item.conf['roto_stop']):
            
            if (item_source() == UP):
                roto_item.roto_step_up()
            else:
                roto_item.roto_step_down()

        if (source == item.conf['roto_up_down']):
            if (item_source() == UP):
                roto_item.roto_up_total()
            else:
                roto_item.roto_down_total()
                
        if (source == item.conf['roto_position']):
            value = 0
            if caller != 'Eval':
                value = item()
            else:
                value = orig_item()
            logger.debug("roto set position: {0}".format(value))
            roto_item.roto_position(value)
			
	
        
    # determine original caller/source
    # smarthome: instance of smarthome.py
    # caller: caller
    # source: source
    def get_original_caller(self, smarthome, caller, source, item=None):
        original_caller = caller
        original_source = source
        original_item = item
        while original_caller == "Eval":
            original_item = smarthome.return_item(original_source)
            if original_item is None:
                break
            original_changed_by = original_item.changed_by()
            if ":" not in original_changed_by:
                break
            original_caller, __, original_source = original_changed_by.partition(":")
        if item is None:
            return original_caller, original_source
        else:
            return original_caller, original_source, original_item
            
  
# Class
class RotoItem:
    # return item id
    @property
    def id(self):
        return self.__id
    
    # time counter
    @property
    def time_on(self):
        return self.__time_on
    
    @time_on.setter
    def time_on(self, value):
        self.__time_on = value
        
    # time counter
    @property
    def time_off(self):
        return self.__time_off
    
    @time_off.setter
    def time_off(self, value):
        self.__time_off = value
        
    @property
    def time_up(self):
        return self.__time_up
    
    @property
    def time_down(self):
        return self.__time_down
    
    @property
    def time_step(self):
        return self.__time_step
    
        
    @property
    def item_up(self):
        return self.__item_up
    
    @property
    def item_down(self):
        return self.__item_down
        
    # time counter
    @property
    def position(self):
        return self.__position
    
    @position.setter
    def position(self, value):
        self.__position = value

    # return instance of smarthome.py class
    @property
    def sh(self):
        return self.__sh

    # Constructor
    # smarthome: instance of smarthome.py
    # item: item to use
    def __init__(self, smarthome, item):
        self.__sh = smarthome
        self.__item = item
        self.__id = self.__item.id()
        self.__name = str(self.__item)
        self.__time_on = self.__sh.now()
        self.__time_off = self.__sh.now()
        self.__time_last_loop = self.__sh.now()
        
        self.__time_up = 60
        if 'roto_time_up' in item.conf:
            self.__time_up = int(item.conf['roto_time_up'])
            
        self.__time_down = 60
        if 'roto_time_down' in item.conf:
            self.__time_down = int(item.conf['roto_time_down'])
        
        self.__cycle_time = 5
        if 'roto_cycle_time' in item.conf:
            self.__cycle_time = int(item.conf['roto_cycle_time'])

        self.__time_step = 10
        if 'roto_time_step' in item.conf:
            self.__time_step = int(item.conf['roto_time_step'])

        if 'roto_actor_open' in item.conf and 'roto_actor_close' in item.conf:
            self.__item_up = self.__sh.return_item(item.conf['roto_actor_up'])
            self.__item_down = self.__sh.return_item(item.conf['roto_actor_down'])
            self.__actor_type = 'roto'
        elif 'roto_actor_up_down' in item.conf and 'roto_actor_stop' in item.conf:
            self.__item_up = self.__sh.return_item(item.conf['roto_actor_up_down'])
            self.__item_down = self.__sh.return_item(item.conf['roto_actor_stop'])
            self.__actor_type = 'jalousie'
        else:
            logger.error("roto Aktor-Items fehlen oder fehlerhaft")
           
        if 'roto_position' in item.conf:
            self.__item_position = self.__sh.return_item(item.conf['roto_position'])
        else:
            logger.error("roto Positions-Items fehlt oder fehlerhaft")
        
        self.__delays = []

        self.__position = self.__item_position()
        self.__position_time = self.__time_up / 100 * self.__position
        self.__direction = OFF
        
    def roto_position(self, value):
        if self.__direction != OFF:
            self.roto_stop()
            time.sleep(IMPULS+1)
            if self.__direction != OFF:
                logger.info("roto Position kann nicht angefahren werden da der Antrieb bereits faehrt: {0}".format(self.__position))
                return
                
        new_pos = value
        old_pos = self.__position
        
        # Auffahren
        if new_pos > old_pos:
            diff_pos = new_pos - old_pos
            diff_time = self.__time_up / 100 * diff_pos
            self.roto_down(diff_time)
            
        #Zufahren:
        elif new_pos < old_pos:
            diff_pos = old_pos - new_pos
            diff_time = self.__time_down / 100 * diff_pos
            self.roto_up(diff_time)

    def roto_up(self, value):
        if self.__direction != OFF:
            self.roto_stop()
        else:
            if self.__actor_type == 'roto':
                self.__item_down(0)
                self.__item_up(1)
                self.__direction = UP
                self.__time_on = self.__sh.now()
                self.__time_last_loop = self.__sh.now()
                self.roto_add_delay(UP, 0, IMPULS)
                self.roto_add_delay(UP, 1, value)
                self.roto_add_delay(UP, 0, value + IMPULS)
            elif self.__actor_type == 'jalousie':
                self.__item_up(UP)
                self.__direction = UP
                self.__time_on = self.__sh.now()
                self.__time_last_loop = self.__sh.now()
                self.roto_add_delay(DOWN, 1, value)

    def roto_down(self, value):
        if self.__direction != OFF:
            self.roto_stop()
        else:
            if self.__actor_type == 'roto':
                self.__item_up(0)
                self.__item_down(1)
                self.__direction = DOWN
                self.__time_on = self.__sh.now()
                self.__time_last_loop = self.__sh.now()
                self.roto_add_delay(DOWN, 0, IMPULS)
                self.roto_add_delay(DOWN, 1, value)
                self.roto_add_delay(DOWN, 0, value + IMPULS)
            elif self.__actor_type == 'jalousie':
                self.__item_up(DOWN)
                self.__direction = DOWN
                self.__time_on = self.__sh.now()
                self.__time_last_loop = self.__sh.now()
                self.roto_add_delay(DOWN, 1, value)

    def roto_up_total(self):
        self.roto_up(self.__time_up)
        
    def roto_down_total(self):
        self.roto_down(self.__time_down)
        
    def roto_step_up(self):
        self.roto_up(self.__time_step)

    def roto_step_down(self):
        self.roto_down(self.__time_step)
            
    def roto_stop(self):
        if self.__actor_type == 'roto':
            if self.__direction == UP:
                self.__item_down(0)
                self.__item_up(1)
                logger.debug("roto_stop Fahrt-AUS Position: {0}".format(self.__position))
                self.__delays = []
                self.roto_add_delay(UP, 0, IMPULS)
                
            if self.__direction == DOWN:
                self.__item_up(0)
                self.__item_down(1)
                logger.debug("roto_stop Fahrt-AUS Position: {0}".format(self.__position))
                self.__delays = []
                self.roto_add_delay(DOWN, 0, IMPULS)
        elif self.__actor_type == 'jalousie':
            if self.__direction is not OFF:
                self.__item_down(1)
                logger.debug("roto_stop Fahrt-AUS Position: {0}".format(self.__position))
                self.__delays = []
                self.__direction = OFF
            
        
    def roto_add_delay(self, direction, value, delay):

        x_delay = {}
        x_delay.update({'delay': delay})
        x_delay.update({'direction': direction})
        x_delay.update({'value': value})
        self.__delays.append(x_delay)
        logger.debug("roto_add_delay: {0}".format(x_delay))
        
        if self.__id not in self.__sh.scheduler:
            s = self.__sh.scheduler.add(self.__id, self.roto_loop, prio=5, offset = 2, cycle=int(self.__cycle_time))

    # wird ueber scheduler aufgerufen
    def roto_loop(self):
        # Wenn keine Eintraege vorhanden sind, kann scheduler deaktiviert werden
        if (len(self.__delays)) == 0:
            if self.__id in self.__sh.scheduler:
                logger.debug("roto_loop STOP scheduler")
                self.__sh.scheduler.remove(self.__id)
                self.__direction = OFF
            else:
                logger.debug("roto_loop keine Eintraege in delays vorhanden")
        else:
            time_on_sec = (self.__sh.now() - self.__time_on).total_seconds()
            # delays-Liste sortieren
            from operator import itemgetter
            x_delays = [x for x in self.__delays]
            
            x_delays.sort(key=itemgetter('delay'), reverse=False)
            if len(x_delays) > 0: 
                x_delay = x_delays[0]
            else:
                logger.debug("roto_loop keine Eintraege in x_delays vorhanden")
                return
            
            # Berechnen der Position Ueber die Fahrzeit
            self.roto_calc_pos()
            self.__time_last_loop = self.__sh.now()
            logger.debug("roto_loop Position: {0}".format(self.__position))
            
            # Impuls ausschalten
            if x_delay['value'] == 0 and time_on_sec > x_delay['delay']:
                if self.__direction == UP:
                    self.__item_up(x_delay['value'])
                elif self.__direction == DOWN:
                    self.__item_down(x_delay['value'])
                else:
                    self.__item_up(0)
                    self.__item_down(0)
                self.__delays.remove(x_delay)
                logger.debug("roto_loop Impuls-AUS Position: {0}".format(self.__position))
            
            #Fahrt aus
            elif self.__direction != OFF and x_delay['value'] == 1 and time_on_sec > x_delay['delay']:
                if self.__actor_type == 'roto': # Impuls geben fuer Fahr aus
                    if self.__direction == UP:
                        self.__item_up(x_delay['value'])
                    elif self.__direction == DOWN:
                        self.__item_down(x_delay['value'])
                    self.__time_off = self.__sh.now()
                    self.__direction = OFF
                    self.__delays.remove(x_delay)
                    logger.debug("roto_loop Fahrt-AUS Position: {0} ".format(self.__position))
                elif self.__actor_type == 'jalousie':
                    if x_delay['direction'] == DOWN:
                        self.__item_down(x_delay['value'])
                        self.__time_off = self.__sh.now()
                        self.__direction = OFF
                        self.__delays.remove(x_delay)
                        logger.debug("roto_loop Fahrt-AUS Position: {0} ".format(self.__position))

    def roto_calc_pos(self):
        time_loop_sec = (self.__sh.now() - self.__time_last_loop).total_seconds()
        if self.__time_on > self.__time_off:
            if self.__direction == DOWN:
                self.__position_time += time_loop_sec
                if self.__position_time > self.__time_up:
                    self.__position_time = self.__time_up
                self.__position = self.__position_time * 100 / self.__time_up
                
            elif self.__direction == UP:
                self.__position_time -= time_loop_sec
                if self.__position_time < 0:
                    self.__position_time = 0
                self.__position = self.__position_time * 100 / self.__time_down
            self.__item_position(self.__position, caller=IDENTICICATION) # aktualisiere das Item
            return self.__position
        else:
            logger.error("roto aktuelle Position konnte nicht berechnet werden: {0} {1} ".format(self.__time_on, self.__time_off))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = Roto('smarthome-dummy')
    myplugin.run()
