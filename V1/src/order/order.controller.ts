import { Controller, Post, Get, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBody } from '@nestjs/swagger';

import { OrderService } from './order.service';

import { CreateTakeAwayOrderDto } from './dto/create-takeaway-order.dto';
import { CreateShippingOrderDto } from './dto/create-shipping-order.dto';
import { CreateEatInOrderDto } from './dto/create-eatin-order.dto';

@ApiTags('órdenes') // Etiqueta para la documentación Swagger
@Controller('orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @ApiOperation({ summary: 'Crear una orden para llevar' })
  @ApiResponse({ status: 201, description: 'La orden para llevar ha sido creada exitosamente.' })
  @ApiBody({ type: CreateTakeAwayOrderDto })
  @Post('takeaway')
  createTakeAway(@Body() dto: CreateTakeAwayOrderDto) {
    return this.orderService.createTakeAway(dto);
  }

  @ApiOperation({ summary: 'Crear una orden con envío a domicilio' })
  @ApiResponse({ status: 201, description: 'La orden con envío ha sido creada exitosamente.' })
  @ApiBody({ type: CreateShippingOrderDto })
  @Post('shipping')
  createShipping(@Body() dto: CreateShippingOrderDto) {
    return this.orderService.createShipping(dto);
  }

  @ApiOperation({ summary: 'Crear una orden para comer en el lugar' })
  @ApiResponse({ status: 201, description: 'La orden para comer en el lugar ha sido creada exitosamente.' })
  @ApiBody({ type: CreateEatInOrderDto })
  @Post('eatin')
  createEatIn(@Body() dto: CreateEatInOrderDto) {
    return this.orderService.createEatIn(dto);
  }

  @ApiOperation({ summary: 'Obtener todas las órdenes para llevar' })
  @ApiResponse({ status: 200, description: 'Lista de órdenes para llevar.' })
  @Get('takeaway')
  findAllTakeAway() {
    return this.orderService.findAllTakeAway();
  }

  @ApiOperation({ summary: 'Obtener todas las órdenes con envío' })
  @ApiResponse({ status: 200, description: 'Lista de órdenes con envío.' })
  @Get('shipping')
  findAllShipping() {
    return this.orderService.findAllShipping();
  }

  @ApiOperation({ summary: 'Obtener todas las órdenes para comer en el lugar' })
  @ApiResponse({ status: 200, description: 'Lista de órdenes para comer en el lugar.' })
  @Get('eatin')
  findAllEatIn() {
    return this.orderService.findAllEatIn();
  }
}

