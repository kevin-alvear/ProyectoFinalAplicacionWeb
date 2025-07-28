import { Controller, Post, Body, Get, Query, Delete, Param } from '@nestjs/common';
import { BookingService } from './booking.service';
import { CreateBookingDto } from './dto/create-booking.dto';
import { ApiTags, ApiOperation, ApiQuery, ApiParam } from '@nestjs/swagger';

@ApiTags('reservas')
@Controller('reservas')
export class BookingController {
  constructor(private readonly bookingService: BookingService) {}

  @Post()
  @ApiOperation({ summary: 'Crear una nueva reserva' })
  create(@Body() dto: CreateBookingDto) {
    return this.bookingService.create(dto);
  }

  @Get('mis-reservas')
  @ApiOperation({ summary: 'Obtener reservas por número de teléfono' })
  @ApiQuery({ name: 'phoneNumber', required: true, description: 'Número telefónico del cliente' })
  findByPhone(@Query('phoneNumber') phone: string) {
    return this.bookingService.findByPhone(phone);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Eliminar reserva por ID' })
  @ApiParam({ name: 'id', description: 'ID de la reserva a eliminar' })
  remove(@Param('id') id: string) {
    return this.bookingService.remove(+id);
  }
}
