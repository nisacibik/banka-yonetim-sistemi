import React, { useState } from 'react';
import { Calculator, Home, Car, User, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const Hesaplama = () => {
  const [selectedKrediTuru, setSelectedKrediTuru] = useState('bireysel');
  const [formData, setFormData] = useState({
    kredi_tutari: '',
    vade_ay: '',
    faiz_orani: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showPlan, setShowPlan] = useState(false);

  // Senin kodundaki tüm kredi türlerini ve ikonlarını koruyoruz
  const krediTurleri = [
    {
      id: 'bireysel',
      title: 'Bireysel Krediler',
      icon: User,
      description: 'İhtiyaç kredisi hesaplaması',
      color: '#3498db'
    },
    {
      id: 'konut',
      title: 'Konut Kredileri',
      icon: Home,
      description: 'Ev kredisi hesaplaması',
      color: '#2ecc71'
    },
    {
      id: 'tasit',
      title: 'Taşıt Kredileri',
      icon: Car,
      description: 'Araç kredisi hesaplaması',
      color: '#9b59b6'
    }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (result) {
      setResult(null);
      setError('');
      setShowPlan(false);
    }
  };

  // Senin o meşhur detaylı ödeme planı fonksiyonun!
  const calculatePaymentPlan = (krediTutari, vadeAy, faizOrani) => {
    const aylikFaizOrani = faizOrani / 100 / 12;
    const aylikTaksit = result.aylik_taksit;
    let kalanAnapara = krediTutari;
    const plan = [];
    
    for (let i = 1; i <= vadeAy; i++) {
      const odenenFaiz = kalanAnapara * aylikFaizOrani;
      const odenenAnapara = aylikTaksit - odenenFaiz;
      kalanAnapara = kalanAnapara - odenenAnapara;
      
      plan.push({
        taksitNo: i,
        taksitTutari: aylikTaksit,
        odenenAnapara: odenenAnapara,
        odenenFaiz: odenenFaiz,
        kalanAnapara: Math.max(0, kalanAnapara)
      });
    }
    return plan;
  };

  const formatNumber = (number) => {
    if (isNaN(number)) return '0,00';
    return new Intl.NumberFormat('tr-TR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(number);
  };

  const handleHesapla = async () => {
    setError('');
    const { kredi_tutari, vade_ay, faiz_orani } = formData;
    
    if (!kredi_tutari || !vade_ay || faiz_orani === '') {
      setError('Lütfen tüm alanları doldurunuz.');
      return;
    }

    setLoading(true);
    
    try {
      // Senin matematiksel formüllerini buraya aldım
      const krediTutari = parseFloat(kredi_tutari);
      const vadeAy = parseInt(vade_ay);
      const faizOrani = parseFloat(faiz_orani);
      const aylikFaizOrani = faizOrani / 100 / 12;

      let aylikTaksit = (krediTutari * aylikFaizOrani * Math.pow(1 + aylikFaizOrani, vadeAy)) / (Math.pow(1 + aylikFaizOrani, vadeAy) - 1);
      const toplamOdeme = aylikTaksit * vadeAy;
      const toplamFaiz = toplamOdeme - krediTutari;

      setResult({
        aylik_taksit: aylikTaksit,
        toplam_odeme: toplamOdeme,
        toplam_faiz: toplamFaiz,
        kredi_tutari: krediTutari,
        vade_ay: vadeAy,
        faiz_orani: faizOrani
      });
    } catch (err) {
      setError('Hesaplama hatası oluştu.');
    } finally {
      setLoading(false);
    }
  };

return (
    <div className="component-container">
      <div className="header-section">
        <Calculator size={36} color="#3498db" />
        <h2>Kredi Hesaplama</h2>
        <p>İhtiyacınıza uygun kredi türünü seçerek taksitlerinizi görün.</p>
      </div>

      <div className="form-wrapper">
        <div className="form-grid-3" style={{ marginBottom: '30px' }}>
          {krediTurleri.map((k) => (
            <div 
              key={k.id} 
              onClick={() => setSelectedKrediTuru(k.id)}
              style={{
                padding: '20px', borderRadius: '12px', border: `2px solid ${selectedKrediTuru === k.id ? k.color : '#eee'}`,
                textAlign: 'center', cursor: 'pointer', background: selectedKrediTuru === k.id ? `${k.color}10` : 'white'
              }}
            >
              <k.icon size={32} color={k.color} style={{ marginBottom: '10px' }} />
              <h4 style={{ margin: 0 }}>{k.title}</h4>
            </div>
          ))}
        </div>

        <div className="form-grid-2">
          <div className="form-group">
            <label>Kredi Tutarı (TL)</label>
            <input type="number" value={formData.kredi_tutari} onChange={(e) => setFormData({...formData, kredi_tutari: e.target.value})} placeholder="Örn: 50000" />
          </div>
          <div className="form-group">
            <label>Vade (Ay)</label>
            <input type="number" value={formData.vade_ay} onChange={(e) => setFormData({...formData, vade_ay: e.target.value})} placeholder="Örn: 36" />
          </div>
        </div>

        <div className="form-group">
          <label>Aylık Faiz Oranı (%)</label>
          <input type="number" value={formData.faiz_orani} onChange={(e) => setFormData({...formData, faiz_orani: e.target.value})} placeholder="Örn: 2.50" />
        </div>

        {error && <div className="error-badge">{error}</div>}

        <button className="login-button" onClick={handleHesapla} disabled={loading}>
          {loading ? <Loader2 className="spinner" /> : 'Hesapla'}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: '30px', padding: '20px', background: '#f8fafc', borderRadius: '12px', textAlign: 'center' }}>
          <h3 style={{ color: '#2c3e50', margin: '0 0 10px 0' }}>Hesaplama Sonucu</h3>
          <div className="form-grid-2">
            <div><p>Aylık Taksit</p><h3>₺{result.aylik_taksit.toLocaleString('tr-TR', { maximumFractionDigits: 2 })}</h3></div>
            <div><p>Toplam Geri Ödeme</p><h3>₺{result.toplam_odeme.toLocaleString('tr-TR', { maximumFractionDigits: 2 })}</h3></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Hesaplama;