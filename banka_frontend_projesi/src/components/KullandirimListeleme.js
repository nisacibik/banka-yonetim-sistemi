import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { List, Database } from 'lucide-react'; // Database buraya eklendi

const KullandirimListeleme = () => {
    const [krediler, setKrediler] = useState([]);
    const [yukleniyor, setYukleniyor] = useState(true);

    useEffect(() => {
        const verileriGetir = async () => {
            try {
                const token = localStorage.getItem('authToken');
                const response = await axios.get('http://127.0.0.1:8000/api/kredi/hesap/', {
                    headers: { Authorization: `Token ${token}` }
                });
                setKrediler(response.data);
            } catch (error) {
                console.error("Hata:", error);
            } finally {
                setYukleniyor(false);
            }
        };
        verileriGetir();
    }, []);

    if (yukleniyor) return (
        <div className="component-container" style={{textAlign: 'center'}}>
            <Database className="spinner" size={40} color="#3498db" />
            <p>Yükleniyor...</p>
        </div>
    );

    return (
        <div className="component-container">
            <div className="header-section">
                <List size={32} />
                <h1>Kredi Kullandırım Listesi</h1>
            </div>
            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr><th>Hesap No</th><th>Müşteri No</th><th>Tutar</th><th>Durum</th></tr>
                    </thead>
                    <tbody>
                        {krediler.map((k) => (
                            <tr key={k.kredi_hesap_no}>
                                <td>{k.kredi_hesap_no}</td>
                                <td>{k.musteri_no}</td>
                                <td>{k.kredi_tutari} {k.doviz_cinsi}</td>
                                <td><span className="status-badge status-active">Aktif</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default KullandirimListeleme;