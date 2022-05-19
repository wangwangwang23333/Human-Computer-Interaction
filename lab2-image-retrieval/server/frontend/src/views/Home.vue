<template>
  <div class="home">

    <el-button 
    type="primary" plain
    icon="el-icon-star-off"
    class="favorite-button"
    @click="openCollection"
    @changeCollect="getCollection"
    :disabled="collectDialogVisible"
    >收藏</el-button>
    <img src="@/assets/search.png"
    width="40%"
    style="position: absolute; left: 0%; top: 0%;"
    />
    <img src="@/assets/plant.png"
    width="10%"
    style="position: absolute; right: 4%; top: -5%;"
    />
    <div style="margin-top: 5%;">

      <UploadImage v-bind:fileList="fileList" ref="uploadImage" @uploadSuccess="uploadSuccess" />
      <el-button 
      :icon="isSearching ? 'el-icon-loading' : 'el-icon-search'" 
      :disabled="fileList.length == 0 || isSearching" 
      @click="searchRes" type="warning"
        style="margin-top: 2%; z-index: 1000;" circle></el-button>
    </div>

    <el-divider></el-divider>


    <BlankPage v-if="responseImage.length == 0" style="z-index:100"/>
    <div v-else>
      <el-row>
        <el-col :span="18">
          <div style="width: 90%;margin:0 auto" class="containerFlex">
            <div v-for="(item,index) in responseImage" :key="index">
              <ImageCard :imageUrl="item" 
              :disallowedTags = "disallowedTags"
              :hideTags="true"
              :imageId="item" />
            </div>

          </div>
        </el-col>
        <el-col :span="1">
          <el-divider direction="vertical"></el-divider>
        </el-col>
        <el-col :span="5">
          <!--tag列表-->
          <div class="label-list">

            <div
            v-for="(item,index) in tags"
            :key="index"
            >
              <el-tag
              :type="labelColor[index % labelColor.length]"
              :hit="true">
              <el-checkbox v-model="item.status" 
              @change = "tagChange"
              />
              {{item.label}}({{item.size}})
              </el-tag>
            </div>                    

        </div>
        </el-col>
      </el-row>


    </div>

    <!--收藏界面-->
    <el-dialog
      title="Collection"
      :visible.sync="collectDialogVisible"
      :close-on-click-modal="false"
      :modal-append-to-body="false"
      width="65%"
      >
      <div v-loading="isCollectionLoading">
        <div style="margin:0 auto" class="containerFlex"
        v-if="collectImage.length != 0">
          <div v-for="(item,index) in collectImage.slice((currentPage-1)*3,currentPage*3)" :key="index">
            <ImageCard :imageUrl="item" 
            :disallowedTags = "disallowedTags"
            :hideTags="false"
            :imageId="item" />
          </div>
          <!--分页符-->
          
        </div>
        <img v-else
        src="@/assets/404_images/no_collect.png"
        width="50%"
        />
      </div>
      <el-pagination
          background
          layout="prev, pager, next"
          :hide-on-single-page="true"
          :page-size="3"
          @current-change="handleCurrentChange"
          :total="collectImage.length">
        </el-pagination>

    </el-dialog>

  </div>
</template>

<script>
import UploadImage  from '@/components/UploadImage.vue';
import ImageCard from '@/components/ImageCard.vue';
import BlankPage from '@/components/BlankPage.vue';
import axios from 'axios';

export default {
  name: 'Home',
  components: {
    UploadImage,
    ImageCard,
    BlankPage
  },
  data(){
    return {
      labelColor: ["", "success", "info", "warning", "danger"],
      fileList: [],
      responseImage: [],
      filterImage: [],
      tags: [],
      disallowedTags: [],
      collectImage: [],
      collectDialogVisible: false,
      currentPage: 1,
      isSearching: false,
      isCollectionLoading: false,
    }
  },
  created(){
    axios({
      method: 'get',
      url: 'tags',
    }).then(response => {
      this.tags = response.data.map((item) => {
        item.status = true;
        return item;
      })
      this.disallowedTags = [];
    }).catch(() => {

    })
    
  },
  methods: {
    uploadSuccess(response) {
      this.responseImage = response;
      this.isSearching = false;
    },
    searchRes() {
      this.isSearching = true;
      this.$refs.uploadImage.submitUpload();
    },
    tagChange() {
      let disallowedTags = [];
      this.tags.forEach(item => {
        if (!item.status) {
          disallowedTags.push(item.label);
        }
      });
      this.disallowedTags = disallowedTags;
    },
    openCollection() {
      this.getCollection();
      this.collectDialogVisible = true;
    },
    handleCurrentChange(val) {
      this.currentPage = val;
    },
    getCollection(){
      this.isCollectionLoading = true;
      axios({
        method: 'get',
        url: 'collect/all',
      }).then(response => {
        this.collectImage = response.data;
      }).catch(() => {

      }).finally(()=>{
        this.isCollectionLoading = false;
      })
    }
  },
}
</script>

<style scoped>

.containerFlex {
    display: flex;
    flex-direction: row;
    /*容器内成员的排列方式为从左到右*/
    flex-wrap: wrap;
    /*换行方式，放不下就换行*/
    justify-content: flex-start;
    /*项目在主轴上的对齐方式*/
    align-content: flex-start;
}



.el-divider--vertical {
    height: 60em !important;
    width: 1.5px !important;
}
.el-tag{
    float:left;
    white-space: pre-line;
    word-break: break-all;
    margin-top: 5px;
    margin-left: 5px;

}
.favorite-button{
  position: fixed;
  bottom: 5%;
  right: 5%;
  z-index: 999999;
  border-radius: 20px;
}
</style>