import React, { useState, useEffect } from 'react';
import { 
  User, 
  Briefcase, 
  Building2, 
  Plus, 
  X, 
  Save, 
  RotateCcw, 
  Phone, 
  Users,
  ShieldCheck,
  Loader2 // <-- Bunu ekledik, hata bitecek!
} from 'lucide-react';


const MusteriTanim = () => {
    const [musteriTuru, setMusteriTuru] = useState('bireysel');
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        vergi_numarasi: '', vergi_dairesi: '', tckn: '', adi: '', soyadi: '',
        dogum_tarihi: '', cinsiyet: '', medeni_hal: '', meslek: '',
        nace_kodu: '', isletme_unvani: '', is_adresi: '', oda_kaydi: '',
        sirket_unvani: '', sirket_turu: '', kurulus_tarihi: '', ticaret_sicil_no: '',
        sirket_nace_kodu: '', yetkili_adi: '', yetkili_soyadi: '', yetkili_tckn: '',
        yetkili_gorevi: '', yetkili_temsil_yetkisi: '',
        telefonlar: [{ telefon: '', telefon_tipi: 'cep' }],
        emailler: [{ email: '', email_tipi: 'kisisel' }],
        adresler: [{ adres: '', adres_tipi: 'ev' }],
        ortaklar: [{ adSoyad: '', pay: '', tckn: '' }]
    });

    // 1. Güvenlik Kontrolü
    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (!token) {
            alert('Giriş yapmanız gerekiyor. Personel giriş sayfasına yönlendiriliyorsunuz.');
            window.location.href = '/';
        }
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleMusteriTuruChange = (tur) => {
        setMusteriTuru(tur);
        // Formu temizle ama yapıları koru
        setFormData({
            vergi_numarasi: '', vergi_dairesi: '', tckn: '', adi: '', soyadi: '',
            dogum_tarihi: '', cinsiyet: '', medeni_hal: '', meslek: '',
            nace_kodu: '', isletme_unvani: '', is_adresi: '', oda_kaydi: '',
            sirket_unvani: '', sirket_turu: '', kurulus_tarihi: '', ticaret_sicil_no: '',
            sirket_nace_kodu: '', yetkili_adi: '', yetkili_soyadi: '', yetkili_tckn: '',
            yetkili_gorevi: '', yetkili_temsil_yetkisi: '',
            telefonlar: [{ telefon: '', telefon_tipi: 'cep' }],
            emailler: [{ email: '', email_tipi: 'kisisel' }],
            adresler: [{ adres: '', adres_tipi: 'ev' }],
            ortaklar: [{ adSoyad: '', pay: '', tckn: '' }]
        });
    };

    // Dinamik Alan Yönetimi (Telefon, Email, Adres, Ortak)
    const addField = (field, template) => setFormData(p => ({ ...p, [field]: [...p[field], template] }));
    const removeField = (field, index) => setFormData(p => ({ ...p, [field]: p[field].filter((_, i) => i !== index) }));
    const updateField = (field, index, subField, value) => {
        setFormData(p => ({
            ...p,
            [field]: p[field].map((item, i) => i === index ? { ...item, [subField]: value } : item)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('authToken');
        setIsLoading(true);
        
        const submitData = { musteri_turu: musteriTuru, ...formData };

        // Temizlik ve Filtreleme (Orijinal Mantık Korundu)
        Object.keys(submitData).forEach(key => {
            if (submitData[key] === '' || submitData[key] === null) delete submitData[key];
        });
        if (submitData.telefonlar) submitData.telefonlar = submitData.telefonlar.filter(t => t.telefon);
        if (submitData.emailler) submitData.emailler = submitData.emailler.filter(e => e.email);
        if (submitData.adresler) submitData.adresler = submitData.adresler.filter(a => a.adres);
        if (submitData.ortaklar) submitData.ortaklar = submitData.ortaklar.filter(o => o.adSoyad && o.pay);

        try {
            const response = await fetch('http://localhost:8000/api/musteri/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`
                },
                body: JSON.stringify(submitData),
            });
            const responseData = await response.json();
            if (response.ok) {
                alert('Müşteri başarıyla kaydedildi!');
                handleMusteriTuruChange(musteriTuru);
            } else {
                alert(`Hata: ${JSON.stringify(responseData.errors || responseData.detail)}`);
            }
        } catch (error) {
            alert('Bağlantı hatası!');
        } finally {
            setIsLoading(false);
        }
    };

    const renderIletisimBolumu = () => (
        <div className="info-card-gray" style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                <Phone size={20} color="#3498db" />
                <h3 style={{ margin: 0 }}>İletişim ve Adres Bilgileri</h3>
            </div>
            
            <div className="form-grid-2">
                <div>
                    <label>Telefonlar</label>
                    {formData.telefonlar.map((tel, i) => (
                        <div key={i} className="dynamic-input-group">
                            <input type="tel" value={tel.telefon} onChange={e => updateField('telefonlar', i, 'telefon', e.target.value)} placeholder="05XX XXX XX XX" />
                            <select value={tel.telefon_tipi} onChange={e => updateField('telefonlar', i, 'telefon_tipi', e.target.value)}>
                                <option value="cep">Cep</option>
                                <option value="is">İş</option>
                            </select>
                            {i > 0 && <X className="remove-icon" onClick={() => removeField('telefonlar', i)} />}
                        </div>
                    ))}
                    <button type="button" className="btn-add-small" onClick={() => addField('telefonlar', { telefon: '', telefon_tipi: 'cep' })}><Plus size={14}/> Telefon Ekle</button>
                </div>

                <div>
                    <label>E-posta Adresleri</label>
                    {formData.emailler.map((email, i) => (
                        <div key={i} className="dynamic-input-group">
                            <input type="email" value={email.email} onChange={e => updateField('emailler', i, 'email', e.target.value)} placeholder="ornek@banka.com" />
                            {i > 0 && <X className="remove-icon" onClick={() => removeField('emailler', i)} />}
                        </div>
                    ))}
                    <button type="button" className="btn-add-small" onClick={() => addField('emailler', { email: '', email_tipi: 'kisisel' })}><Plus size={14}/> E-posta Ekle</button>
                </div>
            </div>

            <div style={{ marginTop: '20px' }}>
                <label>Adresler</label>
                {formData.adresler.map((adr, i) => (
                    <div key={i} className="dynamic-input-group" style={{ marginBottom: '10px' }}>
                        <textarea style={{ flex: 3 }} value={adr.adres} onChange={e => updateField('adresler', i, 'adres', e.target.value)} placeholder="Tam adres..." rows="2" />
                        <select style={{ flex: 1 }} value={adr.adres_tipi} onChange={e => updateField('adresler', i, 'adres_tipi', e.target.value)}>
                            <option value="ev">Ev</option>
                            <option value="is">İş</option>
                        </select>
                        {i > 0 && <X className="remove-icon" onClick={() => removeField('adresler', i)} />}
                    </div>
                ))}
                <button type="button" className="btn-add-small" onClick={() => addField('adresler', { adres: '', adres_tipi: 'ev' })}><Plus size={14}/> Adres Ekle</button>
            </div>
        </div>
    );

    return (
        <div className="component-container">
            <div className="header-section">
                <UserSearch size={32} />
                <h1>Müşteri Tanımlama Portalı</h1>
                <p>Yeni müşteri kaydı ve ticari bilgi girişi</p>
            </div>

            <div className="musteri-tur-tabs-pro">
                <button className={musteriTuru === 'bireysel' ? 'active' : ''} onClick={() => handleMusteriTuruChange('bireysel')}><User size={18}/> Bireysel</button>
                <button className={musteriTuru === 'tfgk' ? 'active' : ''} onClick={() => handleMusteriTuruChange('tfgk')}><Briefcase size={18}/> TFGK</button>
                <button className={musteriTuru === 'tuzel' ? 'active' : ''} onClick={() => handleMusteriTuruChange('tuzel')}><Building2 size={18}/> Tüzel</button>
            </div>

            <form onSubmit={handleSubmit} className="form-wrapper">
                {/* ŞARTLI FORM ALANLARI */}
                {musteriTuru !== 'tuzel' ? (
                    <div className="info-card-white">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}><ShieldCheck size={20} color="#27ae60"/> <h3 style={{ margin: 0 }}>Şahıs / Kimlik Bilgileri</h3></div>
                        <div className="form-grid-3">
                            <div className="form-group"><label>T.C. Kimlik No *</label><input type="text" name="tckn" value={formData.tckn} onChange={handleInputChange} maxLength="11" required /></div>
                            <div className="form-group"><label>Adı *</label><input type="text" name="adi" value={formData.adi} onChange={handleInputChange} required /></div>
                            <div className="form-group"><label>Soyadı *</label><input type="text" name="soyadi" value={formData.soyadi} onChange={handleInputChange} required /></div>
                        </div>
                        <div className="form-grid-3" style={{ marginTop: '15px' }}>
                            <div className="form-group"><label>Doğum Tarihi</label><input type="date" name="dogum_tarihi" value={formData.dogum_tarihi} onChange={handleInputChange} /></div>
                            <div className="form-group"><label>Cinsiyet</label><select name="cinsiyet" value={formData.cinsiyet} onChange={handleInputChange}><option value="">Seçiniz</option><option value="Erkek">Erkek</option><option value="Kadın">Kadın</option></select></div>
                            <div className="form-group"><label>Meslek</label><input type="text" name="meslek" value={formData.meslek} onChange={handleInputChange} /></div>
                        </div>
                    </div>
                ) : (
                    <div className="info-card-white">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}><Building2 size={20} color="#3498db"/> <h3 style={{ margin: 0 }}>Şirket Kurumsal Bilgileri</h3></div>
                        <div className="form-group"><label>Şirket Unvanı *</label><input type="text" name="sirket_unvani" value={formData.sirket_unvani} onChange={handleInputChange} required /></div>
                        <div className="form-grid-2" style={{ marginTop: '15px' }}>
                            <div className="form-group"><label>Şirket Türü</label><select name="sirket_turu" value={formData.sirket_turu} onChange={handleInputChange}><option value="">Seçiniz</option><option value="Limited">Limited</option><option value="Anonim">Anonim</option></select></div>
                            <div className="form-group"><label>Ticaret Sicil No</label><input type="text" name="ticaret_sicil_no" value={formData.ticaret_sicil_no} onChange={handleInputChange} /></div>
                        </div>
                    </div>
                )}

                {/* TİCARİ ALANLAR (TFGK ve Tüzel için ortak) */}
                {musteriTuru !== 'bireysel' && (
                    <div className="info-card-white" style={{ marginTop: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}><Briefcase size={20} color="#f39c12"/> <h3 style={{ margin: 0 }}>Ticari Vergi Bilgileri</h3></div>
                        <div className="form-grid-2">
                            <div className="form-group"><label>Vergi Numarası *</label><input type="text" name="vergi_numarasi" value={formData.vergi_numarasi} onChange={handleInputChange} maxLength="10" required /></div>
                            <div className="form-group"><label>Vergi Dairesi *</label><input type="text" name="vergi_dairesi" value={formData.vergi_dairesi} onChange={handleInputChange} required /></div>
                        </div>
                    </div>
                )}

                {/* ORTAKLAR BÖLÜMÜ (Sadece Tüzel) */}
                {musteriTuru === 'tuzel' && (
                    <div className="info-card-gray" style={{ marginTop: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}><Users size={20}/> <h3 style={{ margin: 0 }}>Ortaklar ve Pay Dağılımı</h3></div>
                        {formData.ortaklar.map((ort, i) => (
                            <div key={i} className="dynamic-input-group" style={{ marginBottom: '10px' }}>
                                <input style={{ flex: 2 }} placeholder="Ad Soyad" value={ort.adSoyad} onChange={e => updateField('ortaklar', i, 'adSoyad', e.target.value)} />
                                <input style={{ flex: 1 }} placeholder="Pay %" type="number" value={ort.pay} onChange={e => updateField('ortaklar', i, 'pay', e.target.value)} />
                                {i > 0 && <X className="remove-icon" onClick={() => removeField('ortaklar', i)} />}
                            </div>
                        ))}
                        <button type="button" className="btn-add-small" onClick={() => addField('ortaklar', { adSoyad: '', pay: '', tckn: '' })}><Plus size={14}/> Ortak Ekle</button>
                    </div>
                )}

                {renderIletisimBolumu()}

                <div className="form-actions" style={{ marginTop: '30px' }}>
                    <button type="submit" className="login-button" disabled={isLoading}>
                        {isLoading ? <Loader2 className="spinner" /> : <><Save size={18}/> Müşteriyi Kaydet</>}
                    </button>
                    <button type="button" className="btn-secondary" onClick={() => handleMusteriTuruChange(musteriTuru)}>
                        <RotateCcw size={16} /> Formu Sıfırla
                    </button>
                </div>
            </form>
        </div>
    );
};

// Müşteri Arama İkonu için küçük helper
const UserSearch = ({ size }) => <Users size={size} />;

export default MusteriTanim;