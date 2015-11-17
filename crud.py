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
            tile = panorama[:, i/n_tiles*im_width:(i+1)/n_tiles*im_width, :]
            imsave(tile_path, tile)

        # insert into SQL using erika's commands
        c = self.conn.cursor()
        for i in range(n_tiles):
            try:
                c.execute("INSERT INTO {tn} ({idf}, {cn}) VALUES ('{map_coord}', '{tile_path}')".\
                    format(tn=self.table_name, idf=self.id_column, cn="tile_%d" % i, map_coord=coord, tile_path=os.path.join(self.local_path, "%s_%d.jpg" % (coord, i))))
            except sqlite3.IntegrityError:
                print('ERROR: ID already exists in PRIMARY KEY column {}'.format(self.id_column))

        self.conn.commit()

    def load_panorama(coord, theta, n_tiles=10):
        """
        Parameters
        ----------
        coord: 3 coordinate tuple
        theta: angle UI is facing
        width: tile width (default 36)
        """
        # figure out from the theta, which is the left and right bounds of the viewing window
        # map_coord_reborn = [int(e) for e in map_coord.strip('()').split(',')]
        pass

if __name__ == '__main__':
    sqlite_file = 'data/neato_street_view.sqlite'    # name of the sqlite database file
    path_to_save_panoramas = 'data/imgs'
    orm = DBWrapper(sqlite_file, path_to_save_panoramas)