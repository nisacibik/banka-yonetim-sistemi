import React, { useState, useRef } from 'react';

const Giris = ({ onLogin }) => {
    const [personelKodu, setPersonelKodu] = useState('');
    const [sifre, setSifre] = useState('');
    const [hata, setHata] = useState('');
    const [yukleniyor, setYukleniyor] = useState(false);
    const isSubmitting = useRef(false);

    const handleLogin = async () => {
        if (isSubmitting.current || yukleniyor) return;
        if (!personelKodu.trim() || !sifre.trim()) {
            setHata('Personel kodu ve şifre gereklidir');
            return;
        }

        isSubmitting.current = true;
        setHata(''); 
        setYukleniyor(true);

        try {
            const requestData = {
                personel_kodu: personelKodu.trim(),
                password: sifre.trim()  
            };

            const response = await fetch('http://127.0.0.1:8000/api/personel/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });

            const data = await response.json();

            if (response.ok) {
                if (data.token) {
                    localStorage.setItem('authToken', data.token);
                }
                onLogin(data);
            } else {
                setHata(data.error || data.detail || 'Giriş başarısız');
            }
        } catch (error) {
            setHata('Sunucuya bağlanılamadı. Backend çalışıyor mu?');
        } finally {
            setTimeout(() => {
                setYukleniyor(false);
                isSubmitting.current = false;
            }, 1000);
        }
    };

    // ESLint uyarısını çözen ve Enter tuşuyla girişi sağlayan kısım
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    };

    return (
        <div className="login-page">
            <div className="component-container" style={{maxWidth: '450px', margin: '0', padding: '50px'}}>
                <div className="header-section">
                    <h2 style={{fontSize: '28px', color: '#2c3e50'}}>Sistem Girişi</h2>
                    <p>Banka Yönetim Portalı</p>
                </div>
                <div className="form-group">
                    <label>Personel Kodu</label>
                    <input type="text" value={personelKodu} onChange={(e) => setPersonelKodu(e.target.value)} onKeyPress={handleKeyPress} placeholder="Kullanıcı Adı" />
                </div>
                <div className="form-group">
                    <label>Şifre</label>
                    <input type="password" value={sifre} onChange={(e) => setSifre(e.target.value)} onKeyPress={handleKeyPress} placeholder="******" />
                </div>
                {hata && <div style={{color: '#e74c3c', marginBottom: '15px', fontWeight: '600'}}>{hata}</div>}
                <button className="login-button" onClick={handleLogin} disabled={yukleniyor}>
                    {yukleniyor ? 'Bağlanıyor...' : 'Giriş Yap'}
                </button>
            </div>
        </div>
    );
};

export default Giris;