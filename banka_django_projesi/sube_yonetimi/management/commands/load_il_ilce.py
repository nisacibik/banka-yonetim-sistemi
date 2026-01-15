# sube_yonetimi/management/commands/load_il_ilce.py
from django.core.management.base import BaseCommand
from sube_yonetimi.models import Il, Ilce

class Command(BaseCommand):
    help = 'Türkiye il ve ilçe verilerini veritabanına yükle'

    def handle(self, *args, **options):
        self.stdout.write('İl ve İlçe verileri yükleniyor...')

        # Türkiye'nin tüm illeri ve önemli ilçeleri
        il_ilce_data = {
          '01': {
        'il_adi': 'Adana',
        'ilceler': ['Merkez', 'Seyhan', 'Yüreğir', 'Çukurova', 'Sarıçam', 'Aladağ', 'Ceyhan', 'Feke', 'İmamoğlu', 'Karaisalı', 'Karataş', 'Kozan', 'Pozantı', 'Saimbeyli', 'Tufanbeyli', 'Yumurtalık']
        },
            '02': {
                'il_adi': 'Adıyaman',
                'ilceler': ['Merkez', 'Besni', 'Çelikhan', 'Gerger', 'Gölbaşı', 'Kahta', 'Samsat', 'Sincik', 'Tut']
            },
            '03': {
                'il_adi': 'Afyonkarahisar',
                'ilceler': ['Merkez', 'Başmakçı', 'Bayat', 'Bolvadin', 'Çay', 'Çobanlar', 'Dazkırı', 'Dinar', 'Emirdağ', 'Evciler', 'Hocalar', 'İhsaniye', 'İscehisar', 'Kızılören', 'Sandıklı', 'Sinanpaşa', 'Sultandağı', 'Şuhut']
            },
            '04': {
                'il_adi': 'Ağrı',
                'ilceler': ['Merkez', 'Diyadin', 'Doğubayazıt', 'Eleşkirt', 'Hamur', 'Patnos', 'Taşlıçay', 'Tutak']
            },
            '05': {
                'il_adi': 'Amasya',
                'ilceler': ['Merkez', 'Göynücek', 'Gümüşhacıköy', 'Hamamözü', 'Merzifon', 'Suluova', 'Taşova']
            },
            '06': {
                'il_adi': 'Ankara',
                'ilceler': ['Altındağ', 'Ayaş', 'Bala', 'Beypazarı', 'Çamlıdere', 'Çankaya', 'Çubuk', 'Elmadağ', 'Etimesgut', 'Evren', 'Gölbaşı', 'Güdül', 'Haymana', 'Kalecik', 'Kazan', 'Keçiören', 'Kızılcahamam', 'Mamak', 'Nallıhan', 'Polatlı', 'Pursaklar', 'Sincan', 'Şereflikoçhisar', 'Yenimahalle']
            },
            '07': {
                'il_adi': 'Antalya',
                'ilceler': ['Aksu', 'Alanya', 'Demre', 'Döşemealtı', 'Elmalı', 'Finike', 'Gazipaşa', 'Gündoğmuş', 'İbradı', 'Kaş', 'Kemer', 'Kepez', 'Konyaaltı', 'Korkuteli', 'Kumluca', 'Manavgat', 'Muratpaşa', 'Serik']
            },
            '08': {
                'il_adi': 'Artvin',
                'ilceler': ['Merkez', 'Ardanuç', 'Arhavi', 'Borçka', 'Hopa', 'Murgul', 'Şavşat', 'Yusufeli']
            },
            '09': {
                'il_adi': 'Aydın',
                'ilceler': ['Merkez', 'Bozdoğan', 'Buharkent', 'Çine', 'Didim', 'Germencik', 'İncirliova', 'Karacasu', 'Karpuzlu', 'Koçarlı', 'Köşk', 'Kuşadası', 'Kuyucak', 'Nazilli', 'Söke', 'Sultanhisar', 'Yenipazar']
            },
            '10': {
                'il_adi': 'Balıkesir',
                'ilceler': ['Altıeylül', 'Ayvalık', 'Balya', 'Bandırma', 'Bigadiç', 'Burhaniye', 'Dursunbey', 'Edremit', 'Erdek', 'Gömeç', 'Gönen', 'Havran', 'İvrindi', 'Karesi', 'Kepsut', 'Manyas', 'Marmara', 'Savaştepe', 'Sındırgı', 'Susurluk']
            },
            '11': {
                'il_adi': 'Bilecik',
                'ilceler': ['Merkez', 'Bozüyük', 'Gölpazarı', 'İnhisar', 'Osmaneli', 'Pazaryeri', 'Söğüt', 'Yenipazar']
            },
            '12': {
                'il_adi': 'Bingöl',
                'ilceler': ['Merkez', 'Adaklı', 'Genç', 'Karlıova', 'Kiğı', 'Solhan', 'Yayladere', 'Yedisu']
            },
            '13': {
                'il_adi': 'Bitlis',
                'ilceler': ['Merkez', 'Adilcevaz', 'Ahlat', 'Güroymak', 'Hizan', 'Mutki', 'Tatvan']
            },
            '14': {
                'il_adi': 'Bolu',
                'ilceler': ['Merkez', 'Dörtdivan', 'Gerede', 'Göynük', 'Kıbrıscık', 'Mengen', 'Mudurnu', 'Seben', 'Yeniçağa']
            },
            '15': {
                'il_adi': 'Burdur',
                'ilceler': ['Merkez', 'Ağlasun', 'Altınyayla', 'Bucak', 'Çavdır', 'Çeltikçi', 'Gölhisar', 'Karamanlı', 'Kemer', 'Tefenni', 'Yeşilova']
            },
            '16': {
                'il_adi': 'Bursa',
                'ilceler': ['Büyükorhan', 'Gemlik', 'Gürsu', 'Harmancık', 'İnegöl', 'İznik', 'Karacabey', 'Keles', 'Kestel', 'Mudanya', 'Mustafakemalpaşa', 'Nilüfer', 'Orhaneli', 'Orhangazi', 'Osmangazi', 'Yenişehir', 'Yıldırım']
            },
            '17': {
                'il_adi': 'Çanakkale',
                'ilceler': ['Merkez', 'Ayvacık', 'Bayramiç', 'Biga', 'Bozcaada', 'Çan', 'Eceabat', 'Ezine', 'Gelibolu', 'Gökçeada', 'Lapseki', 'Yenice']
            },
            '18': {
                'il_adi': 'Çankırı',
                'ilceler': ['Merkez', 'Atkaracalar', 'Bayramören', 'Çerkeş', 'Eldivan', 'Ilgaz', 'Kızılırmak', 'Korgun', 'Kurşunlu', 'Orta', 'Şabanözü', 'Yapraklı']
            },
            '19': {
                'il_adi': 'Çorum',
                'ilceler': ['Merkez', 'Alaca', 'Bayat', 'Boğazkale', 'Dodurga', 'İskilip', 'Kargı', 'Laçin', 'Mecitözü', 'Oğuzlar', 'Ortaköy', 'Osmancık', 'Sungurlu', 'Uğurludağ']
            },
            '20': {
                'il_adi': 'Denizli',
                'ilceler': ['Merkez', 'Acıpayam', 'Babadağ', 'Baklan', 'Bekilli', 'Beyağaç', 'Bozkurt', 'Buldan', 'Çal', 'Çameli', 'Çardak', 'Çivril', 'Güney', 'Honaz', 'Kale', 'Merkezefendi', 'Pamukkale', 'Sarayköy', 'Serinhisar', 'Tavas']
            },
            '21': {
                'il_adi': 'Diyarbakır',
                'ilceler': ['Bağlar', 'Bismil', 'Çermik', 'Çınar', 'Çüngüş', 'Dicle', 'Eğil', 'Ergani', 'Hani', 'Hazro', 'Kayapınar', 'Kocaköy', 'Kulp', 'Lice', 'Silvan', 'Sur', 'Yenişehir']
            },
            '22': {
                'il_adi': 'Edirne',
                'ilceler': ['Merkez', 'Enez', 'Havsa', 'İpsala', 'Keşan', 'Lalapaşa', 'Meriç', 'Süloğlu', 'Uzunköprü']
            },
            '23': {
                'il_adi': 'Elazığ',
                'ilceler': ['Merkez', 'Ağın', 'Alacakaya', 'Arıcak', 'Baskil', 'Karakoçan', 'Keban', 'Kovancılar', 'Maden', 'Palu', 'Sivrice']
            },
            '24': {
                'il_adi': 'Erzincan',
                'ilceler': ['Merkez', 'Çayırlı', 'İliç', 'Kemah', 'Kemaliye', 'Otlukbeli', 'Refahiye', 'Tercan', 'Üzümlü']
            },
            '25': {
                'il_adi': 'Erzurum',
                'ilceler': ['Aziziye', 'Aşkale', 'Çat', 'Hınıs', 'Horasan', 'İspir', 'Karaçoban', 'Karayazı', 'Köprüköy', 'Narman', 'Oltu', 'Olur', 'Palandöken', 'Pasinler', 'Pazaryolu', 'Şenkaya', 'Tekman', 'Tortum', 'Uzundere', 'Yakutiye']
            },
            '26': {
                'il_adi': 'Eskişehir',
                'ilceler': ['Alpu', 'Beylikova', 'Çifteler', 'Günyüzü', 'Han', 'İnönü', 'Mahmudiye', 'Mihalgazi', 'Mihalıççık', 'Odunpazarı', 'Sarıcakaya', 'Seyitgazi', 'Sivrihisar', 'Tepebaşı']
            },
            '27': {
                'il_adi': 'Gaziantep',
                'ilceler': ['Araban', 'İslahiye', 'Karkamış', 'Nizip', 'Nurdağı', 'Oğuzeli', 'Şahinbey', 'Şehitkamil', 'Yavuzeli']
            },
            '28': {
                'il_adi': 'Giresun',
                'ilceler': ['Merkez', 'Alucra', 'Bulancak', 'Çamoluk', 'Çanakçı', 'Dereli', 'Doğankent', 'Espiye', 'Eynesil', 'Görele', 'Güce', 'Keşap', 'Piraziz', 'Şebinkarahisar', 'Tirebolu', 'Yağlıdere']
            },
            '29': {
                'il_adi': 'Gümüşhane',
                'ilceler': ['Merkez', 'Kelkit', 'Köse', 'Kürtün', 'Şiran', 'Torul']
            },
            '30': {
                'il_adi': 'Hakkâri',
                'ilceler': ['Merkez', 'Çukurca', 'Derecik', 'Şemdinli', 'Yüksekova']
            },
            '31': {
                'il_adi': 'Hatay',
                'ilceler': ['Altınözü', 'Antakya', 'Arsuz', 'Belen', 'Defne', 'Dörtyol', 'Erzin', 'Hassa', 'İskenderun', 'Kırıkhan', 'Kumlu', 'Payas', 'Reyhanlı', 'Samandağ', 'Yayladağı']
            },
            '32': {
                'il_adi': 'Isparta',
                'ilceler': ['Merkez', 'Aksu', 'Atabey', 'Eğirdir', 'Gelendost', 'Gönen', 'Keçiborlu', 'Senirkent', 'Sütçüler', 'Şarkikaraağaç', 'Uluborlu', 'Yalvaç', 'Yenişarbademli']
            },
            '33': {
                'il_adi': 'Mersin',
                'ilceler': ['Akdeniz', 'Anamur', 'Aydıncık', 'Bozyazı', 'Çamlıyayla', 'Erdemli', 'Gülnar', 'Mezitli', 'Mut', 'Silifke', 'Tarsus', 'Toroslar', 'Yenişehir']
            },
            '34': {
                'il_adi': 'İstanbul',
                'ilceler': ['Adalar', 'Arnavutköy', 'Ataşehir', 'Avcılar', 'Bağcılar', 'Bahçelievler', 'Bakırköy', 'Başakşehir', 'Bayrampaşa', 'Beşiktaş', 'Beykoz', 'Beylikdüzü', 'Beyoğlu', 'Büyükçekmece', 'Çatalca', 'Çekmeköy', 'Esenler', 'Esenyurt', 'Eyüpsultan', 'Fatih', 'Gaziosmanpaşa', 'Güngören', 'Kadıköy', 'Kağıthane', 'Kartal', 'Küçükçekmece', 'Maltepe', 'Pendik', 'Sancaktepe', 'Sarıyer', 'Silivri', 'Sultanbeyli', 'Sultangazi', 'Şile', 'Şişli', 'Tuzla', 'Ümraniye', 'Üsküdar', 'Zeytinburnu']
            },
            '35': {
                'il_adi': 'İzmir',
                'ilceler': ['Aliağa', 'Balçova', 'Bayındır', 'Bayraklı', 'Bergama', 'Beydağ', 'Bornova', 'Buca', 'Çeşme', 'Çiğli', 'Dikili', 'Foça', 'Gaziemir', 'Güzelbahçe', 'Karabağlar', 'Karaburun', 'Karşıyaka', 'Kemalpaşa', 'Kınık', 'Kiraz', 'Konak', 'Menderes', 'Menemen', 'Narlıdere', 'Ödemiş', 'Seferihisar', 'Selçuk', 'Tire', 'Torbalı', 'Urla']
            },
            '36': {
                'il_adi': 'Kars',
                'ilceler': ['Merkez', 'Akyaka', 'Arpaçay', 'Digor', 'Kağızman', 'Sarıkamış', 'Selim', 'Susuz']
            },
            '37': {
                'il_adi': 'Kastamonu',
                'ilceler': ['Merkez', 'Abana', 'Ağlı', 'Araç', 'Azdavay', 'Bozkurt', 'Cide', 'Çatalzeytin', 'Daday', 'Devrekani', 'Doğanyurt', 'Hanönü', 'İhsangazi', 'İnebolu', 'Küre', 'Pınarbaşı', 'Seydiler', 'Şenpazar', 'Taşköprü', 'Tosya']
            },
            '38': {
                'il_adi': 'Kayseri',
                'ilceler': ['Akkışla', 'Bünyan', 'Develi', 'Felahiye', 'Hacılar', 'İncesu', 'Kocasinan', 'Melikgazi', 'Özvatan', 'Pınarbaşı', 'Sarıoğlan', 'Sarız', 'Talas', 'Tomarza', 'Yahyalı', 'Yeşilhisar']
            },
            '39': {
                'il_adi': 'Kırklareli',
                'ilceler': ['Merkez', 'Babaeski', 'Demirköy', 'Kofçaz', 'Lüleburgaz', 'Pehlivanköy', 'Pınarhisar', 'Vize']
            },
            '40': {
                'il_adi': 'Kırşehir',
                'ilceler': ['Merkez', 'Akçakent', 'Akpınar', 'Boztepe', 'Çiçekdağı', 'Kaman', 'Mucur']
            },
            '41': {
                'il_adi': 'Kocaeli',
                'ilceler': ['Başiskele', 'Çayırova', 'Darıca', 'Derince', 'Dilovası', 'Gebze', 'Gölcük', 'İzmit', 'Kandıra', 'Karamürsel', 'Kartepe', 'Körfez']
            },
            '42': {
                'il_adi': 'Konya',
                'ilceler': ['Ahırlı', 'Akören', 'Akşehir', 'Altınekin', 'Beyşehir', 'Bozkır', 'Cihanbeyli', 'Çeltik', 'Çumra', 'Derbent', 'Derebucak', 'Doğanhisar', 'Emirgazi', 'Ereğli', 'Guneysinir', 'Hadim', 'Halkapınar', 'Hüyük', 'Ilgın', 'Kadınhanı', 'Karapınar', 'Karatay', 'Karaman', 'Kulu', 'Meram', 'Sarayönü', 'Selçuklu', 'Seydişehir', 'Taşkent', 'Tuzlukçu', 'Yalıhüyük', 'Yunak']
            },
            '43': {
                'il_adi': 'Kütahya',
                'ilceler': ['Merkez', 'Altıntaş', 'Aslanapa', 'Çavdarhisar', 'Domaniç', 'Dumlupınar', 'Emet', 'Gediz', 'Hisarcık', 'Pazarlar', 'Simav', 'Şaphane', 'Tavşanlı']
            },
            '44': {
                'il_adi': 'Malatya',
                'ilceler': ['Merkez', 'Akçadağ', 'Arapgir', 'Arguvan', 'Battalgazi', 'Darende', 'Doğanşehir', 'Doğanyol', 'Hekimhan', 'Kale', 'Kuluncak', 'Pütürge', 'Yazıhan', 'Yeşilyurt']
            },
            '45': {
                'il_adi': 'Manisa',
                'ilceler': ['Merkez', 'Ahmetli', 'Akhisar', 'Alaşehir', 'Demirci', 'Gölmarmara', 'Gördes', 'Kırkağaç', 'Köprübaşı', 'Kula', 'Salihli', 'Sarıgöl', 'Saruhanlı', 'Selendi', 'Soma', 'Şehzadeler', 'Turgutlu', 'Yunusemre']
            },
            '46': {
                'il_adi': 'Kahramanmaraş',
                'ilceler': ['Afşin', 'Andırın', 'Çağlayancerit', 'Dulkadiroğlu', 'Ekinözü', 'Elbistan', 'Göksun', 'Nurhak', 'Onikişubat', 'Pazarcık', 'Türkoğlu']
            },
            '47': {
                'il_adi': 'Mardin',
                'ilceler': ['Artuklu', 'Dargeçit', 'Derik', 'Kızıltepe', 'Mazıdağı', 'Midyat', 'Nusaybin', 'Ömerli', 'Savur', 'Yeşilli']
            },
            '48': {
                'il_adi': 'Muğla',
                'ilceler': ['Bodrum', 'Dalaman', 'Datça', 'Fethiye', 'Kavaklıdere', 'Köyceğiz', 'Marmaris', 'Menteşe', 'Milas', 'Ortaca', 'Seydikemer', 'Ula', 'Yatağan']
            },
            '49': {
                'il_adi': 'Muş',
                'ilceler': ['Merkez', 'Bulanık', 'Hasköy', 'Korkut', 'Malazgirt', 'Varto']
            },
            '50': {
                'il_adi': 'Nevşehir',
                'ilceler': ['Merkez', 'Acıgöl', 'Avanos', 'Derinkuyu', 'Gülşehir', 'Hacıbektaş', 'Kozaklı', 'Ürgüp']
            },
            '51': {
                'il_adi': 'Niğde',
                'ilceler': ['Merkez', 'Altunhisar', 'Bor', 'Çamardı', 'Çiftlik', 'Ulukışla']
            },
            '52': {
                'il_adi': 'Ordu',
                'ilceler': ['Merkez', 'Akkuş', 'Altınordu', 'Aybasti', 'Çamaş', 'Çatalpınar', 'Çaybaşı', 'Fatsa', 'Gölköy', 'Gülyalı', 'Gürgentepe', 'İkizce', 'Kabadüz', 'Kabataş', 'Korgan', 'Kumru', 'Mesudiye', 'Perşembe', 'Ulubey', 'Ünye']
            },
            '53': {
                'il_adi': 'Rize',
                'ilceler': ['Merkez', 'Ardeşen', 'Çamlıhemşin', 'Çayeli', 'Derepazarı', 'Fındıklı', 'Güneysu', 'Hemşin', 'İkizdere', 'İyidere', 'Kalkandere', 'Pazar']
            },
            '54': {
                'il_adi': 'Sakarya',
                'ilceler': ['Adapazarı', 'Akyazı', 'Arifiye', 'Erenler', 'Ferizli', 'Geyve', 'Hendek', 'Karapürçek', 'Karasu', 'Kaynarca', 'Kocaali', 'Pamukova', 'Sapanca', 'Serdivan', 'Söğütlü', 'Taraklı']
            },
            '55': {
                'il_adi': 'Samsun',
                'ilceler': ['Atakum', 'Ayvacık', 'Bafra', 'Canik', 'Çarşamba', 'Havza', 'İlkadım', 'Kavak', 'Ladik', 'Ondokuzmayıs', 'Salıpazarı', 'Tekkeköy', 'Terme', 'Vezirköprü', 'Yakakent']
            },
            '56': {
                'il_adi': 'Siirt',
                'ilceler': ['Merkez', 'Baykan', 'Eruh', 'Kurtalan', 'Pervari', 'Şirvan', 'Tillo']
            },
            '57': {
                'il_adi': 'Sinop',
                'ilceler': ['Merkez', 'Ayancık', 'Boyabat', 'Dikmen', 'Durağan', 'Erfelek', 'Gerze', 'Saraydüzü', 'Türkeli']
            },
            '58': {
                'il_adi': 'Sivas',
                'ilceler': ['Merkez', 'Akıncılar', 'Altınyayla', 'Divriği', 'Doğanşar', 'Gemerek', 'Gölova', 'Hafik', 'İmranlı', 'Kangal', 'Koyulhisar', 'Suşehri', 'Şarkışla', 'Ulaş', 'Yıldızeli', 'Zara', 'Gürün']
            },
            '59': {
                'il_adi': 'Tekirdağ',
                'ilceler': ['Çerkezköy', 'Çorlu', 'Ergene', 'Hayrabolu', 'Kapakli', 'Malkara', 'Marmaraereğlisi', 'Muratlı', 'Saray', 'Süleymanpaşa', 'Şarköy']
            },
            '60': {
                'il_adi': 'Tokat',
                'ilceler': ['Merkez', 'Almus', 'Artova', 'Başçiftlik', 'Erbaa', 'Niksar', 'Pazar', 'Reşadiye', 'Sulusaray', 'Turhal', 'Yeşilyurt', 'Zile']
            },
            '61': {
                'il_adi': 'Trabzon',
                'ilceler': ['Akçaabat', 'Araklı', 'Arsin', 'Beşikdüzü', 'Çarşıbaşı', 'Çaykara', 'Dernekpazarı', 'Düzköy', 'Hayrat', 'Köprübaşı', 'Maçka', 'Of', 'Ortahisar', 'Sürmene', 'Şalpazarı', 'Tonya', 'Vakfıkebir', 'Yomra']
            },
            '62': {
                'il_adi': 'Tunceli',
                'ilceler': ['Merkez', 'Çemişgezek', 'Hozat', 'Mazgirt', 'Nazımiye', 'Ovacık', 'Pertek', 'Pülümür']
            },
            '63': {
                'il_adi': 'Şanlıurfa',
                'ilceler': ['Akçakale', 'Birecik', 'Bozova', 'Ceylanpınar', 'Eyyübiye', 'Halfeti', 'Haliliye', 'Harran', 'Hilvan', 'Karaköprü', 'Siverek', 'Suruç', 'Viranşehir']
            },
            '64': {
                'il_adi': 'Uşak',
                'ilceler': ['Merkez', 'Banaz', 'Eşme', 'Karahallı', 'Sivaslı', 'Ulubey']
            },
            '65': {
                'il_adi': 'Van',
                'ilceler': ['Bahçesaray', 'Başkale', 'Çaldıran', 'Çatak', 'Edremit', 'Erciş', 'Gevaş', 'Gürpınar', 'İpekyolu', 'Muradiye', 'Özalp', 'Saray', 'Tuşba']
            },
            '66': {
                'il_adi': 'Yozgat',
                'ilceler': ['Merkez', 'Akdağmadeni', 'Aydıncık', 'Boğazlıyan', 'Çandır', 'Çayıralan', 'Çekerek', 'Kadışehri', 'Saraykent', 'Sarıkaya', 'Sorgun', 'Şefaatli', 'Yenifakılı', 'Yerköy']
            },
            '67': {
                'il_adi': 'Zonguldak',
                'ilceler': ['Merkez', 'Alaplı', 'Çaycuma', 'Devrek', 'Ereğli', 'Gökçebey', 'Kilimli', 'Kozlu']
            },
            '68': {
                'il_adi': 'Aksaray',
                'ilceler': ['Merkez', 'Ağaçören', 'Eskil', 'Gülağaç', 'Güzelyurt', 'Ortaköy', 'Sarıyahşi', 'Sultanhanı']
            },
            '69': {
                'il_adi': 'Bayburt',
                'ilceler': ['Merkez', 'Aydıntepe', 'Demirözü']
            },
            '70': {
                'il_adi': 'Karaman',
                'ilceler': ['Merkez', 'Ayrancı', 'Başyayla', 'Ermenek', 'Kazımkarabekir', 'Sarıveliler']
            },
            '71': {
                'il_adi': 'Kırıkkale',
                'ilceler': ['Merkez', 'Bahşılı', 'Balışeyh', 'Çelebi', 'Delice', 'Karakeçili', 'Keskin', 'Sulakyurt', 'Yahşihan']
            },
            '72': {
                'il_adi': 'Batman',
                'ilceler': ['Merkez', 'Beşiri', 'Gercüş', 'Hasankeyf', 'Kozluk', 'Sason']
            },
            '73': {
                'il_adi': 'Şırnak',
                'ilceler': ['Merkez', 'Beytüşşebap', 'Cizre', 'Güçlükonak', 'İdil', 'Silopi', 'Uludere']
            },
            '74': {
                'il_adi': 'Bartın',
                'ilceler': ['Merkez', 'Amasra', 'Kurucaşile', 'Ulus']
            },
            '75': {
                'il_adi': 'Ardahan',
                'ilceler': ['Merkez', 'Çıldır', 'Damal', 'Göle', 'Hanak', 'Posof']
            },
            '76': {
                'il_adi': 'Iğdır',
                'ilceler': ['Merkez', 'Aralık', 'Karakoyunlu', 'Tuzluca']
            },
            '77': {
                'il_adi': 'Yalova',
                'ilceler': ['Merkez', 'Altınova', 'Armutlu', 'Çınarcık', 'Çiftlikköy', 'Termal']
            },
            '78': {
                'il_adi': 'Karabük',
                'ilceler': ['Merkez', 'Eflani', 'Eskipazar', 'Ovacık', 'Safranbolu', 'Yenice']
            },
            '79': {
                'il_adi': 'Kilis',
                'ilceler': ['Merkez', 'Elbeyli', 'Musabeyli', 'Polateli']
            },
            '80': {
                'il_adi': 'Osmaniye',
                'ilceler': ['Merkez', 'Bahçe', 'Düziçi', 'Hasanbeyli', 'Kadirli', 'Sumbas', 'Toprakkale']
            },
            '81': {
                'il_adi': 'Düzce',
                'ilceler': ['Merkez', 'Akçakoca', 'Cumayeri', 'Çilimli', 'Gölyaka', 'Gümüşova', 'Kaynaşlı', 'Yığılca']
            }

        }

        created_il_count = 0
        created_ilce_count = 0

        for plaka, data in il_ilce_data.items():
            il_adi = data['il_adi']
            
            # İl kodunu da ekle
            il_obj, il_created = Il.objects.get_or_create(
                il_adi=il_adi,
                defaults={'il_kodu': plaka}
            )

            if il_created:
                created_il_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ {il_adi} ({plaka}) ili eklendi.'))
            else:
                # İl kodu eksikse güncelle
                if not il_obj.il_kodu:
                    il_obj.il_kodu = plaka
                    il_obj.save()
                    self.stdout.write(f'→ {il_adi} ({plaka}) ili güncellendi.')
                else:
                    self.stdout.write(f'- {il_adi} ({plaka}) ili zaten mevcut.')
            
            # İlçe verilerini ekle
            for ilce_adi in data['ilceler']:
                ilce_obj, ilce_created = Ilce.objects.get_or_create(
                    il=il_obj,
                    ilce_adi=ilce_adi
                )
                if ilce_created:
                    created_ilce_count += 1
                    self.stdout.write(f'  ✓ {ilce_adi} ilçesi eklendi.')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('İşlem tamamlandı!'))
        self.stdout.write(self.style.SUCCESS(f'Yeni eklenen il sayısı: {created_il_count}'))
        self.stdout.write(self.style.SUCCESS(f'Yeni eklenen ilçe sayısı: {created_ilce_count}'))
        
        # Toplam sayıları göster
        total_il = Il.objects.count()
        total_ilce = Ilce.objects.count()
        self.stdout.write('')
        self.stdout.write(f'Toplam il sayısı: {total_il}')
        self.stdout.write(f'Toplam ilçe sayısı: {total_ilce}')