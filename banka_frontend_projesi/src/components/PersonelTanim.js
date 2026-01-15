import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PersonelTanim = () => {
    const [formData, setFormData] = useState({ ad: '', soyad: '', tel_no: '', mail: '', sube_kodu: '', rol: '' });
    const [personelList, setPersonelList] = useState([]);
    const [subeList, setSubeList] = useState([]);

    useEffect(() => {
        const fetchInitialData = async () => {
            const token = localStorage.getItem('authToken');
            const headers = { Authorization: `Token ${token}` };
            try {
                const subeRes = await axios.get('http://127.0.0.1:8000/api/sube/subeler/', { headers });
                setSubeList(subeRes.data.filter(s => s.durum === 'A'));
                const perRes = await axios.get('http://127.0.0.1:8000/api/personel/', { headers });
                setPersonelList(perRes.data);
            } catch (e) { console.error(e); }
        };
        fetchInitialData();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('authToken');
        try {
            await axios.post('http://127.0.0.1:8000/api/personel/', formData, { headers: { Authorization: `Token ${token}` } });
            alert("Personel başarıyla kaydedildi!");
            setFormData({ ad: '', soyad: '', tel_no: '', mail: '', sube_kodu: '', rol: '' });
        } catch (e) { alert("Hata oluştu!"); }
    };

    return (
        <div className="component-container">
            <div className="header-section"><h2>Personel Yönetimi</h2></div>
            <div className="form-wrapper">
                <form onSubmit={handleSubmit}>
                    <div className="form-grid-2">
                        <div className="form-group"><label>Ad</label><input type="text" value={formData.ad} onChange={(e) => setFormData({...formData, ad: e.target.value})} required /></div>
                        <div className="form-group"><label>Soyad</label><input type="text" value={formData.soyad} onChange={(e) => setFormData({...formData, soyad: e.target.value})} required /></div>
                    </div>
                    <div className="form-group">
                        <label>Şube</label>
                        <select value={formData.sube_kodu} onChange={(e) => setFormData({...formData, sube_kodu: e.target.value})} required>
                            <option value="">Şube Seçiniz</option>
                            {subeList.map(s => <option key={s.sube_kodu} value={s.sube_kodu}>{s.sube_adi}</option>)}
                        </select>
                    </div>
                    <button type="submit" className="login-button">Kaydet</button>
                </form>
            </div>
            <div className="table-wrapper">
                <table>
                    <thead><tr><th>Kod</th><th>Ad Soyad</th><th>Şube</th></tr></thead>
                    <tbody>{personelList.map(p => (<tr key={p.personel_kodu}><td>{p.personel_kodu}</td><td>{p.ad} {p.soyad}</td><td>{p.sube_kodu}</td></tr>))}</tbody>
                </table>
            </div>
        </div>
    );
};

export default PersonelTanim;