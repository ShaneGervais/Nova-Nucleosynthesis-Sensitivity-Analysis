program batch_iso
  implicit none
  integer :: i, ios_file, ios_line, idx, isom, Aint, nline
  character(len=256) :: fname, line
  real(8) :: Zr, Ar, X
  character(len=8) :: el

  open(20, file="summary.csv", status="replace", action='write')
  write(20, '(A)') "file,isotope,X"

  do i = 0, 99999
    write(fname,'("iso_massf",I5.5,".DAT")') i

    open(10, file=trim(fname), status="old", action="read", iostat=ios_file)
    if (ios_file /= 0) cycle

    nline = 0

    do
      read(10,'(A)',iostat=ios_line) line
      if (ios_line /= 0) exit

      ! Skip comments/headers/blank
      if (len_trim(line) == 0) cycle
      if (line(1:1) == '#') cycle
      if (index(line, "ABUNDANCE_MF") > 0) cycle

      ! Parse data line 
      read(line,*,iostat=ios_line) idx, Zr, Ar, isom, X, el, Aint
      if (ios_line /= 0) cycle

      write(20, '(A,",",A,"-",I0,",",ES16.8)') trim(fname), trim(el), Aint, X
      nline = nline + 1
    end do
    close(10)
  end do

  close(20)
  print *, "Wrote summary.csv"
end program
