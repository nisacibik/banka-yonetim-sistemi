import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Tag, Users, Save, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

const SubeTanim = () => {
  const [formData, setFormData] = useState({
    sube_kodu: '',
    sube_adi: '',
    sube_sinifi: '',
    ilce: ''
  });

  const [iller, setIller] = useState([]);
  const [ilceler, setIlceler] = useState([]);
  const [selectedIl, setSelectedIl] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // 1. İlleri Çek
  useEffect(() => {
    const fetchIller = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch('http://127.0.0.1:8000/api/sube/iller/', {
          headers: { 'Authorization': `Token ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setIller(data);
        }
      } catch (error) { console.error('İller yüklenemedi:', error); }
    };
    fetchIller();
  }, []);

  // 2. İl Değiştiğinde İlçeleri Çek
  useEffect(() => {
    if (selectedIl) {
      const fetchIlceler = async () => {
        try {
          const token = localStorage.getItem('authToken');
          const response = await fetch(`http://127.0.0.1:8000/api/sube/ilceler/?il_id=${selectedIl}`, {
            headers: { 'Authorization': `Token ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            setIlceler(data);
          }
        } catch (error) { console.error('İlçeler yüklenemedi:', error); }
      };
      fetchIlceler();
      setFormData(prev => ({ ...prev, ilce: '' }));
    } else { setIlceler([]); }
  }, [selectedIl]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'il') {
      setSelectedIl(value);
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');

    try {
      const token = localStorage.getItem('authToken');
      const submitData = {
        sube_kodu: formData.sube_kodu.trim().toUpperCase(),
        sube_adi: formData.sube_adi.trim(),
        sube_sinifi: formData.sube_sinifi,
        ilce: formData.ilce
      };
      
      const response = await fetch('http://127.0.0.1:8000/api/sube/subeler/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`
        },
        body: JSON.stringify(submitData)
      });

      const data = await response.json();

      if (response.ok) {
        setSuccessMessage(`Şube başarıyla kaydedildi!`);
        setFormData({ sube_kodu: '', sube_adi: '', sube_sinifi: '', ilce: '' });
        setSelectedIl('');
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setErrors(data);
      }
    } catch (error) {
      setErrors({ general: 'Bir hata oluştu. Lütfen tekrar deneyiniz.' });
    } finally {
      setLoading(false);
    }
  };

  const suggestion = (() => {
    if (selectedIl && formData.sube_sinifi) {
      const selectedIlObj = iller.find(il => il.id.toString() === selectedIl);
      if (selectedIlObj) return `${selectedIlObj.il_kodu}${formData.sube_sinifi}001`;
    }
    return '';
  })();

  const personelSiniri = { '1': 25, '2': 15, '3': 8 }[formData.sube_sinifi] || 0;

  return (
    <div className="component-container">
      <div className="header-section">
        <Building2 size={32} />
        <h1>Şube Tanımlama</h1>
        <p>Sisteme yeni bir banka şubesi ekleyin ve yetki sınırlarını belirleyin.</p>
      </div>

      <div className="form-wrapper">
        {errors.general && <div className="error-badge"><AlertCircle size={16}/> {errors.general}</div>}
        {successMessage && <div className="info-card-success" style={{ marginBottom: '20px' }}><CheckCircle2 size={18}/> {successMessage}</div>}

        <form onSubmit={handleSubmit}>
          {/* Bölüm 1: Kimlik Bilgileri */}
          <div className="info-card-white" style={{ marginBottom: '20px' }}>
            <div className="form-grid-2">
              <div className="form-group">
                <label><Tag size={14}/> Şube Kodu *</label>
                <input
                  type="text"
                  name="sube_kodu"
                  value={formData.sube_kodu}
                  onChange={handleInputChange}
                  placeholder={suggestion || "Örn: 341001"}
                  required
                />
                {suggestion && <span style={{ fontSize: '11px', color: '#3498db' }}>Öneri: {suggestion}</span>}
              </div>
              <div className="form-group">
                <label>Şube Adı *</label>
                <input
                  type="text"
                  name="sube_adi"
                  value={formData.sube_adi}
                  onChange={handleInputChange}
                  placeholder="Örn: Kadıköy Merkez"
                  required
                />
              </div>
            </div>
          </div>

          {/* Bölüm 2: Konum ve Sınıf */}
          <div className="info-card-white">
            <div className="form-grid-2">
              <div className="form-group">
                <label><MapPin size={14}/> İl Seçimi *</label>
                <select name="il" value={selectedIl} onChange={handleInputChange} required>
                  <option value="">İl Seçiniz</option>
                  {iller.map(il => (
                    <option key={il.id} value={il.id}>{il.il_adi} ({il.il_kodu})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>İlçe Seçimi *</label>
                <select name="ilce" value={formData.ilce} onChange={handleInputChange} disabled={!selectedIl} required>
                  <option value="">{selectedIl ? 'İlçe Seçiniz' : 'Önce İl Seçiniz'}</option>
                  {ilceler.map(ilce => (
                    <option key={ilce.id} value={ilce.id}>{ilce.ilce_adi}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '15px' }}>
              <label><Users size={14}/> Şube Sınıfı *</label>
              <select name="sube_sinifi" value={formData.sube_sinifi} onChange={handleInputChange} required>
                <option value="">Sınıf Seçiniz</option>
                <option value="1">1. Sınıf (Büyük) - 25 Personel</option>
                <option value="2">2. Sınıf (Orta) - 15 Personel</option>
                <option value="3">3. Sınıf (Küçük) - 8 Personel</option>
              </select>
              {formData.sube_sinifi && (
                <div className="info-card-gray" style={{ marginTop: '10px', padding: '10px' }}>
                  <Users size={16} /> <strong>Kapasite:</strong> Bu şubede maksimum <strong>{personelSiniri}</strong> personel çalışabilir.
                </div>
              )}
            </div>
          </div>

          <button type="submit" className="login-button" disabled={loading} style={{ marginTop: '30px' }}>
            {loading ? <Loader2 className="spinner" /> : <><Save size={18}/> Şubeyi Kaydet</>}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SubeTanim;