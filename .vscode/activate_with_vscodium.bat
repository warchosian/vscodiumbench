@echo off
:: Active l'environnement conda
call "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\Scripts\activate.bat" %1

:: Ajoute VSCodium au PATH après l'activation conda
set "PATH=G:\WarchoLife\WarchoPortable\PortableCommon\VSCodium\vscodium-1.109.41146\bin;%PATH%"
