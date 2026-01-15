import React, { useState } from 'react';
import './App.css';
import Giris from './components/Giris';
import PersonelTanim from './components/PersonelTanim';
import MusteriTanim from './components/MusteriTanim';
import SubeTanim from './components/SubeTanim';
import Hesaplama from './components/Hesaplama';
import Kullandirim from './components/Kullandirim';
import KullandirimListeleme from './components/KullandirimListeleme';

function App() {
  const [page, setPage] = useState('Personel'); 
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('authToken'));

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsLoggedIn(false);
  };

  return (
    <div className="App">
      {isLoggedIn ? (
        <>
          <header className="App-header">
            <div className="header-top">
              <h1>Banka Yönetim Sistemi</h1>
              <button className="logout-btn" onClick={handleLogout}>Çıkış Yap</button>
            </div>
            <nav className="main-nav">
              <button className={page === 'Personel' ? 'active' : ''} onClick={() => setPage('Personel')}>Personel Tanımlama</button>
              <button className={page === 'Musteri' ? 'active' : ''} onClick={() => setPage('Musteri')}>Müşteri Tanımlama</button>
              <button className={page === 'Sube' ? 'active' : ''} onClick={() => setPage('Sube')}>Şube Tanımlama</button>
              <button className={page === 'Hesaplama' ? 'active' : ''} onClick={() => setPage('Hesaplama')}>Hesaplama</button>
              <button className={page === 'Kullandirim' ? 'active' : ''} onClick={() => setPage('Kullandirim')}>Kullandırım</button>
              <button className={page === 'Liste' ? 'active' : ''} onClick={() => setPage('Liste')}>Kullandırım Listeleme</button>
            </nav>
          </header>

          <main className="App-main">
            {page === 'Personel' && <PersonelTanim />}
            {page === 'Musteri' && <MusteriTanim />}
            {page === 'Sube' && <SubeTanim />}
            {page === 'Hesaplama' && <Hesaplama />}
            {page === 'Kullandirim' && <Kullandirim />}
            {page === 'Liste' && <KullandirimListeleme />}
          </main>
        </>
      ) : (
        <Giris onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;