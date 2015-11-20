"""crud.py is a python script that gives us CRUD access to our database.
I would recommend running this via ipython, i.e.

run crud.py
author: youralien + eweiler
"""
import sqlite3
import os
from skimage.io import imread, imsave
import ipdb

class DBWrapper():

    def __init__(self, sqlite_file, local_path, table_name="panoramas", id_column="map_coordinate"):
        self.table_name = table_name
        self.id_column = id_column
        self.local_path = local_path
        self.conn = sqlite3.connect(sqlite_file)
        print "Opened DB connection"

    def __del__(self):
        self.conn.close()
        print "Closed DB connection"

    def create_table(self, n_tiles=10):
        # Connecting to the database file
        c = self.conn.cursor()

        c.execute('CREATE TABLE {tn} ({nf} TEXT PRIMARY KEY)'\
                .format(tn=self.table_name, nf=self.id_column))

        for i in range(n_tiles):
            # A) Adding a new column without a row value
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' TEXT"\
                    .format(tn=self.table_name, cn="tile_%d" % i))

        self.conn.commit()

    def insert_panorama(self, coord, panorama, n_tiles=10):
        """
        Parameters
        ----------
        coord: 3 coordinate tuple
        panorama: image or filepath
        n_tiles: number of tiles to cut the panorama into (default 10)
        """
        # RCL: should figure out decimal precision of coord
        coord = str(coord)

        if type(panorama) == str:
            panorama = imread(panorama)
        
        if 360 % n_tiles != 0:
            print "Choose n_tiles that divides 360 evenly"
            return

        # crop the panorama
        im_width = panorama.shape[1]
        for i in range(n_tiles):
            i = float(i) # division advantages
            tile_path = os.path.join(self.local_path, "%s_%d.jpg" % (coord, i))
            left = int(i/n_tiles*im_width)
            right = int((i+1)/n_tiles*im_width)
            tile = panorama[:, left:right, :]
            imsave(tile_path, tile)

        # insert into SQL using erika's commands
        c = self.conn.cursor()
        for i in range(n_tiles):
                c.execute("INSERT OR IGNORE INTO {tn} ({idf}, {cn}) VALUES ('{map_coord}', '{tile_path}')".\
                    format(tn=self.table_name, idf=self.id_column, cn="tile_%d" % i, map_coord=coord, tile_path=os.path.join(self.local_path, "%s_%d.jpg" % (coord, i))))
                c.execute("UPDATE {tn} SET {cn}='{tile_path}' WHERE {idf}='{map_coord}'".\
                    format(tn=self.table_name, idf=self.id_column, cn="tile_%d" % i, map_coord=coord, tile_path=os.path.join(self.local_path, "%s_%d.jpg" % (coord, i))))

        self.conn.commit()

    def choose_tile(self,coord, theta, n_tiles=10):
        # print out from the theta which tile the neato is facing
        """
        Parameters
        ----------
        coord: 3 coordinate tuple
        theta: angle UI is facing
        n_tiles: number of tiles (default 10)
        """
        c = self.conn.cursor()
        tilenumber = round(float(theta) / 36)
        tile = 'tile_' + str(int(tilenumber))
        c.execute("SELECT ('{tile}') FROM panoramas WHERE map_coordinate=('{coord}')".\
            format(tile=tile, coord=coord))
        print c.fetchall()

        # map_coord_reborn = [int(e) for e in map_coord.strip('()').split(',')]

if __name__ == '__main__':
    sqlite_file = 'data/neato_street_view.sqlite'    # name of the sqlite database file
    path_to_save_panoramas = 'data/imgs'
    orm = DBWrapper(sqlite_file, path_to_save_panoramas)
    orm.insert_panorama((0, 0, 0), 'data/climbing_panorama.jpg')
    orm.insert_panorama((0, 0, 1), 'data/climbing_panorama.jpg')
    orm.insert_panorama((0, 0, 2), 'data/climbing_panorama.jpg')
    coord = '(0, 0, 1)'
    theta = 70
    orm.choose_tile(coord,theta)