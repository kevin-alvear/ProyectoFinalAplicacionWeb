import { Controller, Get, Post, Body, Patch, Param, Delete } from '@nestjs/common';
import { MenuService } from './menu.service';
import { CreateMenuDto } from './dto/create-menu.dto';
import { UpdateMenuDto } from './dto/update-menu.dto';

import { ApiTags, ApiOperation, ApiResponse, ApiParam } from '@nestjs/swagger';

@ApiTags('Menu')  // Agrupa en Swagger bajo 'Menu'
@Controller('menu')
export class MenuController {
  constructor(private readonly menuService: MenuService) {}

  @Post()
  @ApiOperation({ summary: 'Crear un nuevo ítem del menú' })
  @ApiResponse({ status: 201, description: 'Ítem del menú creado correctamente.' })
  create(@Body() createMenuDto: CreateMenuDto) {
    return this.menuService.create(createMenuDto);
  }

  @Get()
  @ApiOperation({ summary: 'Obtener todos los ítems del menú' })
  @ApiResponse({ status: 200, description: 'Lista de ítems del menú.' })
  findAll() {
    return this.menuService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obtener un ítem del menú por ID' })
  @ApiParam({ name: 'id', description: 'ID del menú', type: Number })
  @ApiResponse({ status: 200, description: 'Ítem del menú encontrado.' })
  @ApiResponse({ status: 404, description: 'Ítem no encontrado.' })
  findOne(@Param('id') id: string) {
    return this.menuService.findOne(+id);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Actualizar un ítem del menú' })
  @ApiParam({ name: 'id', description: 'ID del menú a actualizar', type: Number })
  @ApiResponse({ status: 200, description: 'Ítem actualizado correctamente.' })
  @ApiResponse({ status: 404, description: 'Ítem no encontrado.' })
  update(@Param('id') id: string, @Body() updateMenuDto: UpdateMenuDto) {
    return this.menuService.update(+id, updateMenuDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Eliminar un ítem del menú' })
  @ApiParam({ name: 'id', description: 'ID del menú a eliminar', type: Number })
  @ApiResponse({ status: 200, description: 'Ítem eliminado correctamente.' })
  @ApiResponse({ status: 404, description: 'Ítem no encontrado.' })
  remove(@Param('id') id: string) {
    return this.menuService.remove(+id);
  }
}

