import { Injectable, NotFoundException } from '@nestjs/common'; // Importa NotFoundException para findOne, update, remove
import { InjectRepository } from '@nestjs/typeorm'; // Importa InjectRepository
import { Repository } from 'typeorm'; // Importa Repository
import { Menu } from '../entities/menu.entity'; // Asegúrate de que la ruta sea correcta
import { CreateMenuDto } from './dto/create-menu.dto';
import { UpdateMenuDto } from './dto/update-menu.dto';

@Injectable()
export class MenuService {
  constructor(
    @InjectRepository(Menu) // Inyecta el repositorio de la entidad Menu
    private readonly menuRepository: Repository<Menu>,
  ) {}

  async create(createMenuDto: CreateMenuDto): Promise<Menu> {
    // Crea una nueva instancia de la entidad Menu con los datos del DTO
    const menu = this.menuRepository.create(createMenuDto);
    // Guarda la entidad en la base de datos
    return this.menuRepository.save(menu);
  }

  async findAll(): Promise<Menu[]> {
    // Encuentra y devuelve todos los ítems del menú
    return this.menuRepository.find();
  }

  async findOne(id: number): Promise<Menu> {
    // Busca un ítem del menú por su ID
    const menu = await this.menuRepository.findOneBy({ id });
    if (!menu) {
      // Si no se encuentra, lanza una excepción NotFoundException
      throw new NotFoundException(`Menú con ID ${id} no encontrado.`);
    }
    return menu;
  }

  async update(id: number, updateMenuDto: UpdateMenuDto): Promise<Menu> {
    // Busca el menú por ID
    const menu = await this.menuRepository.findOneBy({ id });
    if (!menu) {
      throw new NotFoundException(`Menú con ID ${id} no encontrado para actualizar.`);
    }

    // Aplica los cambios del DTO al objeto de la entidad
    this.menuRepository.merge(menu, updateMenuDto);

    // Guarda los cambios en la base de datos
    return this.menuRepository.save(menu);
  }

  async remove(id: number): Promise<void> {
    // Busca el menú por ID para asegurar que existe antes de eliminar
    const result = await this.menuRepository.delete(id);
    if (result.affected === 0) {
      // Si no se afectó ninguna fila, significa que el ID no existía
      throw new NotFoundException(`Menú con ID ${id} no encontrado para eliminar.`);
    }
    // No devuelve nada si la eliminación fue exitosa
  }
}
