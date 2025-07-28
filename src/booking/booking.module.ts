import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BookingService } from './booking.service';
import { BookingController } from './booking.controller';
import { Booking } from '../entities/booking.entity';
import { Table } from '../entities/table.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Booking, Table])],
  controllers: [BookingController],
  providers: [BookingService],
})
export class BookingModule {}
