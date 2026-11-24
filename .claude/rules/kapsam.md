# Kapsam

Kullanıcı açıkça bir yol vermedikçe çalışma proje diziniyle sınırlıdır. Bilgisayardaki başka klasör ve dosyalara bakılmaz, yazılmaz.

Kullanıcı bir dosya veya dizin verdiyse iş o yolun içinde kalır. O yolun dışındaki dosya ve klasörlere bakılmaz.

Başka bir yola geçmek için kullanıcının o yolu net olarak söylemesi gerekir.

`.dev/` proje içindedir. Kullanıcı bu yolun içinden bir dosya vermedikçe bakılmaz. İçindeki not kalıcı belge değildir. Kalıcı karar `docs/` altına yazılır. Git'e yalnızca `.dev/README.md` girer.

```text
kötü: Kayıt kuralını okurken ev dizinindeki notlara da bakayım.
iyi: Yalnızca verdiğin docs/kayitlar/degisiklikler.md içindeyim.
```
