#! python3


import sqlite3


#list of tables:

#batch
#samples
#tripletop
#Pcontact
#substtype
#Ncontact
#PkAbsorber
#PkAbsorberMethod
#electrode
#recombjct
#users
#environment
#characsetups
#takencharacsetups
#cells
#eqemeas
#JVmeas
#MPPmeas


#sqlite variable type: TEXT, NULL, INTEGER, REAL, BLOB

def CreateAllTables(db_conn,new):
    
    theCursor = db_conn.cursor()

#%%    
    try:#batch_name (e.g. P999), topic (nip baseline, pin baseline, texture2TT, 4TT...)
        theCursor.execute("""CREATE TABLE IF NOT EXISTS batch(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                batchname TEXT NOT NULL UNIQUE,
                topic TEXT NOT NULL,
                startdate TEXT NOT NULL,
                commentbatch TEXT,
                users_id INTEGER,
                takencharacsetups_id INTEGER,
                FOREIGN KEY(users_id) REFERENCES users(id),
                FOREIGN KEY(takencharacsetups_id) REFERENCES takencharacsetups(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table batch couldn't be created")
    try:#sample_name (e.g. P999_99), sampletype (), cellarchitecture (planar, mesoporous, NULL), polarity (nip, pin, NULL), HTL (...), ETL (...)
        theCursor.execute("""CREATE TABLE IF NOT EXISTS samples(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                samplename TEXT NOT NULL UNIQUE,
                cellarchitecture TEXT,
                reference TEXT,
                samplefullstack TEXT,
                polarity TEXT,
                bottomCellDBRef TEXT,
                commentsamples TEXT,
                tripletop_id INTEGER,
                Pcontact_id INTEGER,
                Ncontact_id INTEGER,
                PkAbsorber_id INTEGER,
                PkAbsorberMethod_id INTEGER,
                substtype_id INTEGER,
                electrode_id INTEGER,
                recombjct_id INTEGER,
                batch_id INTEGER,
                FOREIGN KEY(batch_id) REFERENCES batch(id) ON DELETE CASCADE,
                FOREIGN KEY(electrode_id) REFERENCES electrode(id),
                FOREIGN KEY(substtype_id) REFERENCES substtype(id),
                FOREIGN KEY(Pcontact_id) REFERENCES Pcontact(id),
                FOREIGN KEY(Ncontact_id) REFERENCES Ncontact(id),
                FOREIGN KEY(PkAbsorber_id) REFERENCES PkAbsorber(id),
                FOREIGN KEY(PkAbsorberMethod_id) REFERENCES PkAbsorberMethod(id),
                FOREIGN KEY(tripletop_id) REFERENCES tripletop(id),
                FOREIGN KEY(recombjct_id) REFERENCES recombjct(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table samples couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS tripletop(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                topstack TEXT UNIQUE,
                Pcontact_id INTEGER,
                Ncontact_id INTEGER,
                PkAbsorber_id INTEGER,
                PkAbsorberMethod_id INTEGER,
                electrode_id INTEGER,
                FOREIGN KEY(electrode_id) REFERENCES electrode(id),
                FOREIGN KEY(Pcontact_id) REFERENCES Pcontact(id),
                FOREIGN KEY(Ncontact_id) REFERENCES Ncontact(id),
                FOREIGN KEY(PkAbsorber_id) REFERENCES PkAbsorber(id),
                FOREIGN KEY(PkAbsorberMethod_id) REFERENCES PkAbsorberMethod(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table tripletop couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS Pcontact(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                contactstackP TEXT UNIQUE,
                commentpcontacts TEXT
                )""")
        if new:
            theCursor.executemany("INSERT INTO Pcontact (contactstackP) VALUES (?)",
                            (("NULL",), ("spiro-OMeTAD",),("Poly-TPD/PFN",),("PTAA/PFN",),("Poly-TPD",),("PTAA",),("F4TCNQ-PTAA",),("PTAA/PMMA",),("F4TCNQ-PTAA/PMMA",),("acidicPedot",),("neutralPedot",),("sol-NiOx",),("sput-NiOx",)))
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table Pcontact couldn't be created")    
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS pixelarea(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                pixel_area REAL
                )""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table pixelarea couldn't be created")     
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS substtype(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                substratetype TEXT  UNIQUE,
                commentsubsttype TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO substtype (substratetype) VALUES (?)",
                            (("glass", ),("quartz", ),("silicon", ),("PET", ),("PEN", )))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table substtype couldn't be created")    
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS Ncontact(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                contactstackN TEXT UNIQUE,
                commentncontacts TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO Ncontact (contactstackN) VALUES (?)",
                            (("NULL",), ("C60", ),("LiF/C60",),("C60/PEIE", ),("C60/BCP", ),("LiF/C60/PEIE",),
                             ("C60/aldSnO2/ZTO", ),("LiF/C60/aldSnO2/ZTO",),("C60/PEIE/aldSnO2/ZTO", ),("LiF/C60/PEIE/aldSnO2/ZTO",),
                            ("C60/aldSnO2",),("C60/aldAZO",),("C60/PEIE/aldAZO",)))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table Ncontact couldn't be created") 
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS PkAbsorber(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                absorbercomposition TEXT UNIQUE,
                commentpkabsorber TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO PkAbsorber (absorbercomposition) VALUES (?)",
                            (("NULL",),("FA0.75Cs0.25Sn0.5Pb0.5I3", ),("DMA0.1FA0.6Cs0.3PbI2.4Br0.6", )))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table PkAbsorber couldn't be created")  
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS PkAbsorberMethod(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                absorberMethod TEXT UNIQUE
                );""")
        if new:
            theCursor.executemany("INSERT INTO PkAbsorberMethod (absorberMethod) VALUES (?)",
                            (("NULL",), ("sol-1step-DEE-drip",),("sol-1step-MeOAc-drip",),("sol-1step-N2blow",)))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table PkAbsorberMethod couldn't be created") 
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS electrode(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                electrodestack TEXT UNIQUE,
                commentelectrode TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO electrode (electrodestack) VALUES (?)",
                            (("NULL",), ("Au", ),("Ag", ),("Cu", ),
                             ("IZO-PDIL-LowCond", ),("IZO-PDIL-HighCond", ),("ITO-denton-LowCond", ),("ITO-denton-HighCond", ),
                             ("IZO-PDIL-LowCond/Au", ),("IZO-PDIL-HighCond/Au", ),("ITO-denton-LowCond/Au", ),("ITO-denton-HighCond/Au", )))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table electrode couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS recombjct(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                recombjctstack TEXT UNIQUE,
                commentrecombjct TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO recombjct (recombjctstack) VALUES (?)",
                            (("NULL",), ("IZO-PDIL-LowCond", ),("ITO-denton-LowCond", ),("ITO-racetrack", ),("ITO-XY15s", ),("ITO-XY10s", ) ))
        db_conn.commit()
        
    except sqlite3.OperationalError:
        print("Table recombjct couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                affiliation TEXT NOT NULL,
                email TEXT,
                commentusers TEXT
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table users couldn't be created")
#    try:
#        theCursor.execute("""CREATE TABLE IF NOT EXISTS environment(
#                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                RHyellowroom REAL,
#                RHMC162 REAL,
#                Tempyellowroom REAL,
#                Tempmc162 REAL,
#                gloveboxsolvent REAL,
#                solventGBwatervalue REAL,
#                solventGBoxygenvalue REAL,
#                evapGBwatervalue REAL,
#                evapGBoxygenvalue REAL,
#                commentenvir TEXT
#                );""")
#        db_conn.commit()
#    except sqlite3.OperationalError:
#        print("Table environment couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS characsetups(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                characsetupname TEXT UNIQUE,
                commentcharac TEXT
                );""")
        if new:
            theCursor.executemany("INSERT INTO characsetups (characsetupname) VALUES (?)",
                            (("NULL",), ("SunSimul_C215", ),("SunSimul_cigssetup", ),("EQE_c215", ),("EQE_stf136", ),("SEM", ),("TEM", ),("TofSIMS", ),
                             ("UV-vis-spectro",),("Raman",),("PDS",),("FTPS",),("FTIR",),("Ellipso",),("AFM",),("HallEffect",),
                             ("PL",),("TRPL",),("PLQE",),("PL-imaging",),("ThermoLocking",),("SunsVoc",),("OpticalProfiloMicros.",),("TRMC",),("XRD",),
                             ("SPA-nrel", ),("SPA-stanfordLED", ),("SPA-stanfordPlasma", ),("hotplateC215box", ),))
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table characsetups couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS takencharacsetups(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                takencharacsetupsname TEXT,
                commenttakencharac TEXT
                );""")
    except sqlite3.OperationalError:
        print("Table takencharacsetups couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS cells(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                cellname TEXT,
                samples_id INTEGER,
                pixelarea_id REAL,
                batch_id INTEGER,
                FOREIGN KEY(pixelarea_id) REFERENCES pixelarea(id),
                FOREIGN KEY(batch_id) REFERENCES batch(id) ON DELETE CASCADE,
                FOREIGN KEY(samples_id) REFERENCES samples(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table cells couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS eqemeas(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                EQEmeasname TEXT,
                EQEmeasnameDateTimeEQEJsc TEXT UNIQUE,
                DateTimeEQE TEXT,
                integJsc REAL,
                Eg0 REAL,
                EgIP REAL,
                EgTauc REAL,
                EgLn REAL,
                Vbias TEXT,
                filter TEXT,
                LEDbias TEXT,
                linktofile TEXT,
                commenteqe TEXT,
                samples_id INTEGER,
                batch_id INTEGER,
                cells_id INTEGER,
                FOREIGN KEY(batch_id) REFERENCES batch(id) ON DELETE CASCADE,
                FOREIGN KEY(samples_id) REFERENCES samples(id),
                FOREIGN KEY(cells_id) REFERENCES cells(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table eqemeas couldn't be created")
    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS JVmeas(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                DateTimeJV TEXT,
                Eff REAL,
                Voc REAL,
                Jsc REAL,
                FF REAL,
                Vmpp REAL,
                Jmpp REAL,
                Pmpp REAL,
                Roc REAL,
                Rsc REAL,
                ScanDirect TEXT,
                Delay REAL,
                IntegTime REAL,
                CellArea REAL,
                Vstart REAL,
                Vend REAL,
                Setup TEXT,
                NbPoints REAL,
                ImaxComp REAL,
                Isenserange REAL,
                Operator TEXT,
                GroupJV TEXT,
                IlluminationIntensity REAL,
                commentJV TEXT,
                linktorawdata TEXT UNIQUE,
                aftermpp INTEGER,
                samples_id INTEGER,
                batch_id INTEGER,
                cells_id INTEGER,
                FOREIGN KEY(batch_id) REFERENCES batch(id) ON DELETE CASCADE,
                FOREIGN KEY(samples_id) REFERENCES samples(id),
                FOREIGN KEY(cells_id) REFERENCES cells(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table JVmeas couldn't be created")

    try:
        theCursor.execute("""CREATE TABLE IF NOT EXISTS MPPmeas(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                DateTimeMPP TEXT,
                TrackingAlgo TEXT,
                TrackingDuration REAL,
                Vstart REAL,
                Vstep REAL,
                CellArea REAL,
                Operator TEXT,
                PowerEnd REAL,
                PowerAvg REAL,
                commentmpp TEXT,
                linktorawdata TEXT UNIQUE,
                samples_id INTEGER,
                batch_id INTEGER,
                cells_id INTEGER,
                FOREIGN KEY(batch_id) REFERENCES batch(id) ON DELETE CASCADE,
                FOREIGN KEY(samples_id) REFERENCES samples(id),
                FOREIGN KEY(cells_id) REFERENCES cells(id)
                );""")
        db_conn.commit()
    except sqlite3.OperationalError:
        print("Table MPPmeas couldn't be created")    
#%%


###############################################################################        
if __name__ == '__main__':
    
    db_conn=sqlite3.connect(':memory:')
    
    CreateAllTables(db_conn)  
    
