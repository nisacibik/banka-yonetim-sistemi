import React, { useState, useEffect } from 'react';
import { 
  UserSearch, 
  Wallet, 
  Calendar, 
  Percent, 
  Briefcase, 
  CheckCircle2, 
  Loader2, 
  Search,
  ArrowLeft,
  Info
} from 'lucide-react';

const Kullandirim = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [musteriArama, setMusteriArama] = useState('');
    const [musteriSonuclari, setMusteriSonuclari] = useState([]);
    const [secilenMusteri, setSecilenMusteri] = useState(null);
    const [showMusteriDropdown, setShowMusteriDropdown] = useState(false);
    const [krediFormData, setKrediFormData] = useState({
        kredi_turu: '',
        kredi_tutari: '',
        doviz_cinsi: 'TRY',
        vade: '',
        aylik_faiz_orani: '',
        masraf_tutari: '0'
    });
    const [hesaplananDegerler, setHesaplananDegerler] = useState({
        aylik_odeme: 0,
        toplam_geri_odeme: 0,
        toplam_faiz: 0
    });
    const [odemePlani, setOdemePlani] = useState([]);

    // 1. Güvenlik Kontrolü
    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (!token) {
            alert('Giriş yapmanız gerekiyor. Personel giriş sayfasına yönlendiriliyorsunuz.');
            window.location.href = '/';
        }
    }, []);

    // 2. Müşteri Arama (Debounce Mantığı Korundu)
    useEffect(() => {
        const musteriAra = async () => {
            const token = localStorage.getItem('authToken');
            try {
                const response = await fetch(`http://localhost:8000/api/kredi/musteri-arama/?search=${encodeURIComponent(musteriArama)}`, {
                    headers: { 'Authorization': `Token ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setMusteriSonuclari(data);
                    setShowMusteriDropdown(data.length > 0);
                }
            } catch (error) {
                console.error('Müşteri arama hatası:', error);
            }
        };

        const timeoutId = setTimeout(() => {
            if (musteriArama.length >= 2) {
                musteriAra();
            } else {
                setMusteriSonuclari([]);
                setShowMusteriDropdown(false);
            }
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [musteriArama]);

    // 3. Ödeme Planı Hesaplama (Orijinal Mantık)
    const hesaplaOdemePlani = (krediTutari, vade, aylikFaizOrani) => {
        const plan = [];
        let kalanAnapara = parseFloat(krediTutari);
        const faizOrani = parseFloat(aylikFaizOrani) / 100;
        
        let aylikOdeme;
        if (aylikFaizOrani === 0) {
            aylikOdeme = krediTutari / vade;
        } else {
            const carpan = Math.pow(1 + faizOrani, vade);
            aylikOdeme = (krediTutari * faizOrani * carpan) / (carpan - 1);
        }

        for (let i = 1; i <= vade; i++) {
            const faizTutari = kalanAnapara * faizOrani;
            const anaparaTutari = aylikOdeme - faizTutari;
            kalanAnapara -= anaparaTutari;
            if (i === vade) kalanAnapara = 0;

            plan.push({
                taksitNo: i,
                taksitTutari: aylikOdeme.toFixed(2),
                anaparaTutari: anaparaTutari.toFixed(2),
                faizTutari: faizTutari.toFixed(2),
                kalanAnapara: Math.max(0, kalanAnapara).toFixed(2)
            });
        }
        return plan;
    };

    // 4. Kredi Hesaplama Tetikleyici (Her Değişimde Çalışır)
    useEffect(() => {
        const hesaplaKredi = () => {
            const krediTutari = parseFloat(krediFormData.kredi_tutari) || 0;
            const vade = parseInt(krediFormData.vade) || 0;
            const aylikFaizOrani = parseFloat(krediFormData.aylik_faiz_orani) || 0;
            const masrafTutari = parseFloat(krediFormData.masraf_tutari) || 0;

            if (krediTutari <= 0 || vade <= 0) {
                setOdemePlani([]);
                return;
            }

            let aylikOdeme = 0;
            if (aylikFaizOrani === 0) {
                aylikOdeme = krediTutari / vade;
            } else {
                const faizOrani = aylikFaizOrani / 100;
                const carpan = Math.pow(1 + faizOrani, vade);
                aylikOdeme = (krediTutari * faizOrani * carpan) / (carpan - 1);
            }

            const toplamGeriOdeme = (aylikOdeme * vade) + masrafTutari;
            const toplamFaiz = toplamGeriOdeme - krediTutari - masrafTutari;

            setHesaplananDegerler({
                aylik_odeme: aylikOdeme.toFixed(2),
                toplam_geri_odeme: toplamGeriOdeme.toFixed(2),
                toplam_faiz: toplamFaiz.toFixed(2)
            });

            const plan = hesaplaOdemePlani(krediTutari, vade, aylikFaizOrani);
            setOdemePlani(plan);
        };

        if (krediFormData.kredi_tutari && krediFormData.vade && krediFormData.aylik_faiz_orani) {
            hesaplaKredi();
        } else {
            setHesaplananDegerler({ aylik_odeme: 0, toplam_geri_odeme: 0, toplam_faiz: 0 });
            setOdemePlani([]);
        }
    }, [krediFormData.kredi_tutari, krediFormData.vade, krediFormData.aylik_faiz_orani, krediFormData.masraf_tutari]);

    const musteriSec = (musteri) => {
        setSecilenMusteri(musteri);
        setMusteriArama(musteri.display_name);
        setShowMusteriDropdown(false);
    };

    const handleKrediFormChange = (e) => {
        const { name, value } = e.target;
        setKrediFormData(prev => ({ ...prev, [name]: value }));
    };

    // 5. Kaydetme İşlemi
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!secilenMusteri) { alert('Lütfen bir müşteri seçiniz.'); return; }

        const token = localStorage.getItem('authToken');
        setIsLoading(true);

        const submitData = {
            musteri_no: secilenMusteri.musteri_no,
            ...krediFormData,
            kredi_tutari: parseFloat(krediFormData.kredi_tutari),
            vade: parseInt(krediFormData.vade),
            aylik_faiz_orani: parseFloat(krediFormData.aylik_faiz_orani),
            masraf_tutari: parseFloat(krediFormData.masraf_tutari)
        };

        try {
            const response = await fetch('http://localhost:8000/api/kredi/hesap/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`
                },
                body: JSON.stringify(submitData),
            });

            const responseData = await response.json();

            if (response.ok) {
                alert(`Kredi hesabı başarıyla açıldı!\nHesap No: ${responseData.data.kredi_hesap_no}`);
                setSecilenMusteri(null);
                setMusteriArama('');
                setKrediFormData({ kredi_turu: '', kredi_tutari: '', doviz_cinsi: 'TRY', vade: '', aylik_faiz_orani: '', masraf_tutari: '0' });
            } else {
                alert(`Hata: ${responseData.message || 'İşlem başarısız.'}`);
            }
        } catch (error) {
            alert('Bağlantı hatası!');
        } finally {
            setIsLoading(false);
        }
    };

 return (
        <div className="component-container">
            <div className="header-section">
                <Briefcase size={32} color="#3498db" />
                <h1>Kredi Kullandırımı</h1>
                <p>Müşteri seçimi ve kredi açılış işlemlerini buradan yapabilirsiniz.</p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="form-wrapper" style={{ padding: '20px', background: '#f8fafc', borderRadius: '12px', marginBottom: '25px' }}>
                    <label><Search size={16} /> Müşteri Arama</label>
                    <input 
                        type="text" 
                        value={musteriArama} 
                        onChange={(e) => setMusteriArama(e.target.value)} 
                        placeholder="Müşteri No veya Ad Soyad ile arayın..." 
                    />
                    {musteriSonuclari.length > 0 && !secilenMusteri && (
                        <div style={{ background: 'white', border: '1px solid #ddd', borderRadius: '8px', marginTop: '5px' }}>
                            {musteriSonuclari.map(m => (
                                <div key={m.musteri_no} onClick={() => {setSecilenMusteri(m); setMusteriArama(m.display_name)}} style={{ padding: '10px', cursor: 'pointer', borderBottom: '1px solid #eee' }}>
                                    {m.display_name} ({m.musteri_no})
                                </div>
                            ))}
                        </div>
                    )}
                    {secilenMusteri && (
                        <div style={{ marginTop: '15px', color: '#27ae60', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
                            <CheckCircle2 size={18} /> Müşteri Seçildi: {secilenMusteri.display_name}
                        </div>
                    )}
                </div>

                <div className="form-grid-2">
                    <div className="form-group">
                        <label>Kredi Türü</label>
                        <select value={krediFormData.kredi_turu} onChange={(e) => setKrediFormData({...krediFormData, kredi_turu: e.target.value})} required>
                            <option value="">Seçiniz</option>
                            <option value="ihtiyac">İhtiyaç Kredisi</option>
                            <option value="konut">Konut Kredisi</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Döviz Cinsi</label>
                        <select value={krediFormData.doviz_cinsi} onChange={(e) => setKrediFormData({...krediFormData, doviz_cinsi: e.target.value})}>
                            <option value="TRY">TRY</option>
                            <option value="USD">USD</option>
                        </select>
                    </div>
                </div>

                <div className="form-grid-3">
                    <div className="form-group"><label>Kredi Tutarı</label><input type="number" value={krediFormData.kredi_tutari} onChange={(e) => setKrediFormData({...krediFormData, kredi_tutari: e.target.value})} required /></div>
                    <div className="form-group"><label>Vade (Ay)</label><input type="number" value={krediFormData.vade} onChange={(e) => setKrediFormData({...krediFormData, vade: e.target.value})} required /></div>
                    <div className="form-group"><label>Faiz Oranı (%)</label><input type="number" value={krediFormData.aylik_faiz_orani} onChange={(e) => setKrediFormData({...krediFormData, aylik_faiz_orani: e.target.value})} required /></div>
                </div>

                <button type="submit" className="login-button" disabled={isLoading || !secilenMusteri}>
                    {isLoading ? <Loader2 className="spinner" /> : 'Kredi Hesabı Aç'}
                </button>
            </form>
        </div>
    );
};

export default Kullandirim;