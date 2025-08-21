      dimension Vbu(10000,2002), Ele(10,100), Exp(100), tmp(100)
      integer im(100), ind(100)
      character*15 lab(100), tml(100)
      character*80 line1
      character*200 title
      character*12 Lab_Exp, Lab_Ele(100)
      character(len=5000) :: aString
!
! read  matrix
!
      read(5,'(a200)') Title
      read(5,*) IWrite
      read(5,*) NFlag
      read(5,*) IFlag
      read(5,'(a80)') line1
      read(5,*) NSys
!
! Sanity check
!
      if (NSys.gt.100) stop
!
      read(5,*) NEle
      read(5,*) NSte
      read(5,*) NVbu
      read(5,*) (Lab(i),i=1,NSys)
!
      read(5,'(a)')aString
      k = index(aString, " ")
      Lab_Exp = aString(1:k-1)
      read(aString(k:5000),*)(Exp(i),i=1,NSys)
!
      do j = 1,NEle
        read(5,'(a)')aString
        k = index(aString, " ")
        Lab_Ele(j) = aString(1:k-1)
        read(aString(k:5000),*)(Ele(j,i),i=1,NSys)
      enddo
!
      do j = 1,NVbu
         read(5,*)(Vbu(j,i),i=1,NSte*NSys+2)
      enddo
!
! sort experimental values
!
      do i = 1,100
         im = 0
      enddo
!
      do i = 1,NSys
         xmin = 99999999.99
         do j = 1,NSys
            if (Exp(j).le.xmin .and. im(j).eq.0) then
               imin = j
               xmin = Exp(j)
            endif
         enddo
         im(imin) = 1
         ind(i) = imin
       enddo  
!
!  write reordered matrix
!
      write(6,'(a200)') Title
      write(6,'(i5)') IWrite
      write(6,'(i5)') NFlag
      write(6,'(i5)') IFlag
      write(6,'(a80)') line1
      write(6,'(i5)') NSys
      write(6,'(i5)') NEle
      write(6,'(i5)') NSte - 1
      write(6,'(i5)') 51   
      write(6,'(15x,100a15)') (Lab(i),i=1,NSys)
      write(6,'(a12,100e15.5)')Lab_Exp,(Exp(i),i=1,NSys)
!
      do j = 1,NEle
         write(6,'(a12,100e15.5)')Lab_ELE(j),(Ele(j,i),i=1,NSys)
      enddo
!
      do j = 1,NVbu, 50
         write(6,'(2f6.2,100(x,f14.3))')Vbu(j,1),Vbu(j,2),
     +  (Vbu(j,i),i=3,NSte*NSys+2,2)
      enddo
!
      stop
      end

