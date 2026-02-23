program extract_final_iso
  implicit none
  integer :: idx, isom, ios, n, Aint, i, ios_file, last_i
  real(8) :: Zr, Ar, X
  character(len=8) :: el
  character(len=256) :: line, fname

  last_i = -1
  do i = 0, 99999
    write(fname, '("iso_massf",I5.5,".DAT")') i    
    open(11, file=trim(fname), status="old", action="read", iostat=ios_file)
    if (ios_file == 0) then
      close(11)
      last_i = i
    end if
  end do

  if (last_i < 0) then
    print *, "ERROR: no iso_massf*.DAT files found in current directory."
    stop 1
  end if

  write(fname, '("iso_massf",I5.5,".DAT")') last_i
  print *, "Using final file: ", trim(fname)


  open(10, file=trim(fname), status="old", action="read", iostat=ios)
  if (ios /= 0) then
    print *, "ERROR: could not open ", trim(fname)
    stop 1
  endif

  open(20, file="final_abundances.csv", status="replace", action="write")
  write(20,'(A)') "isotope,X"

  n = 0

  do
    read(10,'(A)',iostat=ios) line
    if (ios /= 0) exit

    ! Skip headers and comments
    if (line(1:1) == '#') cycle
    if (index(line,"ABUNDANCE_MF")>0) cycle
    if (len_trim(line) == 0) cycle

    ! Parse data line
    read(line,*,iostat=ios) idx, Zr, Ar, isom, X, el, Aint
    if (ios /= 0) cycle

    write(20,'(A,"-",I0,",",ES16.8)') trim(el), Aint, X
    n = n + 1
  end do

  close(10)
  close(20)

  print *, "Read ", n, " isotopes."

end program
